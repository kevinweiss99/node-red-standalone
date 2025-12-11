import asyncio
import json
import traceback

import pyaudio
from aiohttp import web, ClientSession

from google import genai
from google.genai import types


system_prompt = "You are the robot Pepper and you are giving a presentation. Always talk in english! The presentation is about Asterix and Obelix. Accordingly, when you receive explicit questions, you should provide only well-founded answers on this topic. For questions on other topics, please point out that the current presentation is about Asterix and Obelix, and you would like to receive only presentation-specific questions. This is the presentation you just gave, you are now answering questions on it: Dear ladies and gentlemen, today I would like to tell you about two of the most famous comic characters ever: Asterix and Obelix. These two heroes come from a small Gallic village that cannot be found on any Roman map and has always been a thorn in the side of the Romans. But this village is not just any village. It is a place full of courage, friendship, and unwavering solidarity. Asterix is the clever and cunning hero of our stories. Despite his rather small stature, he possesses a sharp mind that helps him outsmart the Roman legions time and again. His best friend Obelix, on the other hand, is the exact opposite: big, strong, and always hungry for wild boar. These two complement each other perfectly. Together, they embark on adventures that often go far beyond the borders of their small village.A distinctive feature of the stories is the magic potion made by the druid Getafix, which grants Asterix and his companions superhuman strength. Obelix, however, is a special case: as a child, he fell into the cauldron of the magic potion, which means he is naturally incredibly strong. This strength not only leads to many humorous situations but is also a decisive advantage in battles against the Romans. But the adventures of Asterix and Obelix are much more than just fights. They are full of humor, cultural references, and clever social commentary. The stories often poke fun at the Romans, the Greeks, or other peoples, always with a wink. At the same time, they convey values such as friendship, courage, loyalty, and the power of community. The comics, written by René Goscinny and illustrated by Albert Uderzo, have captivated millions of readers worldwide since their creation in the 1950s. Their popularity has endured across generations because the stories are timeless and appeal to both children and adults. Additionally, the adventures of Asterix and Obelix have been translated into numerous languages, adapted into films, and even brought to life in a theme park. In conclusion, Asterix and Obelix are not just two funny characters in a comic. They stand for courage, cleverness, and the joy of life. They show us that even the smallest among us can achieve great things when we stick together. And perhaps that is the most important lesson we can learn from their adventures."

# system_prompt = "You are Pepper, a talking pepper."

# === Audio / Gemini config ===

FORMAT = pyaudio.paInt16
CHANNELS = 1
SEND_SAMPLE_RATE = 16000
CHUNK_SIZE = 1024

mic_enabled = False

MODEL = "gemini-live-2.5-flash-preview"

client = genai.Client(
    http_options={"api_version": "v1beta"},
    api_key = "secret"
)

CONFIG = types.LiveConnectConfig(
    # TEXT output only
    response_modalities=["TEXT"],
    media_resolution="MEDIA_RESOLUTION_MEDIUM",
    context_window_compression=types.ContextWindowCompressionConfig(
        trigger_tokens=25600,
        sliding_window=types.SlidingWindow(target_tokens=12800),
    ),
    system_instruction=types.Content(
        parts=[types.Part.from_text(text=system_prompt)],
        role="user"
    ),
)

pya = pyaudio.PyAudio()


class AudioLoop:
    def __init__(self):
        self.out_queue: asyncio.Queue | None = None  # audio → Gemini
        self.ws_out_queue: asyncio.Queue | None = None  # text → WebSocket
        self.session = None  # Gemini live session
        self.audio_stream = None
        self.ws_url = "ws://172.30.36.198:1880/speech"

    async def send_realtime(self):
        # Send mic audio chunks to Gemini
        while True:
            msg = await self.out_queue.get()
            # audio=types.Blob(data=msg, mime_type='audio/pcm;rate=16000')
            await self.session.send(input=msg)

    async def listen_audio(self):
        mic_info = pya.get_default_input_device_info()
        self.audio_stream = await asyncio.to_thread(
            pya.open,
            format=FORMAT,
            channels=CHANNELS,
            rate=SEND_SAMPLE_RATE,
            input=True,
            input_device_index=mic_info["index"],
            frames_per_buffer=CHUNK_SIZE,
        )
        kwargs = {"exception_on_overflow": False}

        while True:
            global mic_enabled
            if not mic_enabled:
                await asyncio.sleep(0.5)
                continue

            data = await asyncio.to_thread(self.audio_stream.read, CHUNK_SIZE, **kwargs)
            await self.out_queue.put({"data": data, "mime_type": "audio/pcm"})

    async def receive_text(self):
        # Receive text from Gemini and:
        #  - print to stdout
        #  - forward raw text to WebSocket
        while True:
            turn = self.session.receive()
            async for response in turn:
                if response.text is not None:
                    # Print to console
                    print(response.text, end="", flush=True)

                    # Send to WebSocket as plain text
                    if self.ws_out_queue is not None:
                        await self.ws_out_queue.put(response.text)

    async def ws_sender(self):
        # Maintains a WS connection and sends buffered text messages
        async with ClientSession() as http_session:
            while True:
                try:
                    async with http_session.ws_connect(self.ws_url) as ws:
                        print(f"Connected to WebSocket: {self.ws_url}")
                        loop = asyncio.get_running_loop()

                        while True:
                            # Wait for the first message (blocking)
                            first_text = await self.ws_out_queue.get()
                            buffer = [first_text]
                            last_msg_time = loop.time()

                            # Collect more messages that arrive within 0.5s of the last one
                            while True:
                                elapsed = loop.time() - last_msg_time
                                remaining = 0.5 - elapsed
                                if remaining <= 0:
                                    break

                                try:
                                    next_text = await asyncio.wait_for(
                                        self.ws_out_queue.get(),
                                        timeout=remaining,
                                    )
                                    buffer.append(next_text)
                                    last_msg_time = loop.time()
                                except asyncio.TimeoutError:
                                    # No new message within the remaining window
                                    break

                            # Send the concatenated batch as a single WS frame
                            """ text = "".join(buffer)
                            json = '{"value":"' + str(text.encode("utf-8")) + '"}'
                            await ws.send_str(json) """

                            text = "".join(buffer)
                            payload = {"value": text}
                            await ws.send_str(json.dumps(payload))


                except asyncio.CancelledError:
                    # Task cancelled – exit cleanly
                    break
                except Exception as e:
                    print(f"WebSocket connection error, retrying in 1s: {e}")
                    await asyncio.sleep(1)


    async def run(self):
        try:
            async with (
                client.aio.live.connect(model=MODEL, config=CONFIG) as session,
                asyncio.TaskGroup() as tg,
            ):
                self.session = session
                self.out_queue = asyncio.Queue(maxsize=5)
                self.ws_out_queue = asyncio.Queue()  # no maxsize: avoid backpressure issues

                tg.create_task(self.send_realtime())
                tg.create_task(self.listen_audio())
                tg.create_task(self.receive_text())
                tg.create_task(self.ws_sender())

                # keep running until cancelled
                await asyncio.Future()

        except asyncio.CancelledError:
            print("client disconnected")
        except ExceptionGroup as EG:
            if self.audio_stream is not None:
                self.audio_stream.close()
            traceback.print_exception(EG)


async def enable_microphone_handler(request):
    global mic_enabled
    mic_enabled = True
    print("Microphone ENABLED")
    return web.Response(status=200, text="Mic enabled")


async def disable_microphone_handler(request):
    global mic_enabled
    mic_enabled = False
    print("Microphone DISABLED")
    return web.Response(status=200, text="Mic disabled")


async def main():
    audio_loop = AudioLoop()

    app = web.Application()
    app["audio_loop"] = audio_loop
    app.router.add_post("/mic/enable", enable_microphone_handler)
    app.router.add_post("/mic/disable", disable_microphone_handler)

    runner = web.AppRunner(app)
    await runner.setup()
    local_ip = "172.30.36.223" 
    site = web.TCPSite(runner, local_ip, 8000)
    await site.start()

    print("Mic control endpoints:")
    print(f"  POST http://{local_ip}:8000/mic/enable")
    print(f"  POST http://{local_ip}:8000/mic/disable")
    print("Streaming mic audio → Gemini (TEXT responses printed to stdout and sent via WebSocket).")

    await audio_loop.run()
    await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
