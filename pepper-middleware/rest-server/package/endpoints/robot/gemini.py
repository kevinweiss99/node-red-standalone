from flask import request, Response
import logging
import threading

from ...server import app, socketio
from ...pepper.connection import audio
from ...decorator import log

import asyncio
import traceback

import requests
import numpy as np

from google import genai
from google.genai import types


logger = logging.getLogger(__name__)

# -------------------------------------------------------------------------
# Config
# -------------------------------------------------------------------------

MAX_PEPPER_BUFFER_BYTES = 16384
PEPPER_SAMPLE_RATE = 48000

SEND_SAMPLE_RATE = 16000
RECEIVE_SAMPLE_RATE = 24000

MODEL = "models/gemini-2.5-flash-native-audio-preview-09-2025"

client = genai.Client(
    http_options={"api_version": "v1beta"},
    api_key="secret",  # replace / env var in real code or call endpoint below
)

CONFIG = types.LiveConnectConfig(
    response_modalities=["AUDIO"],
    media_resolution="MEDIA_RESOLUTION_MEDIUM",
    speech_config=types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Aoede")
        )
    ),
    context_window_compression=types.ContextWindowCompressionConfig(
        trigger_tokens=25600,
        sliding_window=types.SlidingWindow(target_tokens=12800),
    ),
    system_instruction=types.Content(
        parts=[types.Part.from_text(
            text="You are a humanoid robot named Salt. Speak concisely and naturally."
        )],
        role="user",
    ),
)


main = None          # type: AudioLoop | None
loop = None          # type: asyncio.AbstractEventLoop | None
loop_thread = None   # type: threading.Thread | None
session_lock = threading.Lock()



def gemini_mono24k_to_pepper_stereo48k(mono_24k_pcm: bytes) -> bytes:
    """Convert 24 kHz mono int16 PCM → 48 kHz stereo interleaved int16 PCM."""
    # 1. Decode to numpy int16 array (mono)
    samples = np.frombuffer(mono_24k_pcm, dtype=np.int16)

    # 2. Upsample 24k → 48k by simple duplication (factor 2).
    upsampled = np.repeat(samples, 2)

    # 3. Duplicate mono to stereo and interleave channels: L,R,L,R,...
    stereo = np.column_stack((upsampled, upsampled)).ravel().astype(np.int16)

    # 4. Back to bytes
    return stereo.tobytes()


def send_buffer_to_pepper(stereo_48k_pcm: bytes):
    """Send a 48 kHz stereo interleaved PCM buffer to Pepper in <=16 KB chunks."""
    logger.debug("sending buffer to pepper of size %d", len(stereo_48k_pcm))

    # Each stereo frame is 4 bytes (2 channels × 2 bytes)
    for offset in range(0, len(stereo_48k_pcm), MAX_PEPPER_BUFFER_BYTES):
        chunk = stereo_48k_pcm[offset:offset + MAX_PEPPER_BUFFER_BYTES]
        if not chunk:
            continue
        nb_frames = len(chunk) // 4
        if nb_frames <= 0:
            continue

        logger.info("sending audio buffer to pepper of size %d", nb_frames)
        audio.sendRemoteBufferToOutput(nb_frames, chunk, _async=True)





# handles Gemini Live session and audio I/O
class AudioLoop:
    def __init__(self):
        self.audio_in_queue: asyncio.Queue[bytes] | None = None
        self.out_queue: asyncio.Queue[dict] | None = None

        self.session = None
        self.stop_event = asyncio.Event()

    async def send_realtime(self):
        """Send raw PCM chunks to Gemini as they come in."""
        assert self.out_queue is not None
        while not self.stop_event.is_set():
            msg = await self.out_queue.get()
            try:
                await self.session.send(input=msg)  # msg is {"data": bytes, "mime_type": "audio/pcm"}
            except Exception:
                logger.exception("Error sending audio chunk to Gemini")
                break

    async def receive_audio(self):
        """Read model outputs and push PCM audio chunks into audio_in_queue."""
        assert self.audio_in_queue is not None
        while not self.stop_event.is_set():
            turn = self.session.receive()
            async for response in turn:
                if data := response.data:
                    # response.data is raw PCM bytes at RECEIVE_SAMPLE_RATE
                    await self.audio_in_queue.put(data)
                    continue
                if text := response.text:
                    # Optional: log transcripts
                    logger.info("Gemini text: %s", text)

            # If you interrupt the model, it sends a turn_complete.
            # Clear any queued audio that's no longer relevant.
            while not self.audio_in_queue.empty():
                try:
                    self.audio_in_queue.get_nowait()
                except asyncio.QueueEmpty:
                    break

    async def play_audio(self):
        """Consume model audio and send it to Pepper."""
        assert self.audio_in_queue is not None
        while not self.stop_event.is_set():
            bytestream = await self.audio_in_queue.get()
            # Convert + send to Pepper
            stereo_48k = gemini_mono24k_to_pepper_stereo48k(bytestream)
            # Run blocking Pepper call in thread so we don't block event loop
            await asyncio.to_thread(send_buffer_to_pepper, stereo_48k)

    async def run(self):
        """Main lifecycle: connect to Gemini and run tasks until stopped."""
        self.audio_in_queue = asyncio.Queue()
        self.out_queue = asyncio.Queue(maxsize=200)

        try:
            async with client.aio.live.connect(model=MODEL, config=CONFIG) as session:
                self.session = session
                logger.info("Gemini Live session started")

                async with asyncio.TaskGroup() as tg:
                    tg.create_task(self.send_realtime())
                    tg.create_task(self.receive_audio())
                    tg.create_task(self.play_audio())

                    # Wait until stop_event is set
                    await self.stop_event.wait()
                    logger.info("Stop event set, cancelling tasks")
                    tg.cancel()
        except Exception as e:
            logger.exception("Error in AudioLoop.run: %s", e)
        finally:
            self.session = None
            logger.info("Gemini Live session ended")

    async def stop(self):
        """Signal the loop to stop."""
        self.stop_event.set()

    async def enqueue_audio(self, pcm_bytes: bytes):
        """Coroutine: push incoming PCM to out_queue for Gemini."""
        if self.out_queue is None:
            return

        try:
            self.out_queue.put_nowait({"data": pcm_bytes, "mime_type": "audio/pcm"})
        except asyncio.QueueFull:
            logger.warning("enqueue_audio: queue full, dropping frame")
            return
        except Exception as e:
            logger.exception("Unexpected error in enqueue_audio")



# Background thread / loop management
def _run_audio_loop():
    """Target function for background thread."""
    global main, loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    main = AudioLoop()
    try:
        loop.run_until_complete(main.run())
    finally:
        loop.close()
        with session_lock:
            # mark as fully stopped
            logger.info("Audio loop thread exiting")
            # main & loop will be set to None in stop handler after join





@socketio.on("/robot/gemini/start")
@app.route("/robot/gemini/start", methods=["POST"])
@log("/robot/gemini/start")
def start_gemini_session():
    """Starts the session with Gemini."""
    global loop_thread, main, loop

    with session_lock:
        if loop_thread is not None and loop_thread.is_alive():
            logger.info("Gemini session already running")
            return Response(status=200)

        # Reset in case anything stale is hanging around
        main = None
        loop = None

        loop_thread = threading.Thread(target=_run_audio_loop, daemon=True)
        loop_thread.start()
        logger.info("Started Gemini audio loop thread")

    return Response(status=200)


@socketio.on("/robot/gemini/stop")
@app.route("/robot/gemini/stop", methods=["POST"])
@log("/robot/gemini/stop")
def stop_gemini_session():
    """Stops the session with Gemini."""
    global loop_thread, main, loop

    with session_lock:
        if loop is None or main is None:
            logger.info("No active Gemini session to stop")
            return Response(status=200)

        # Ask the AudioLoop to stop
        asyncio.run_coroutine_threadsafe(main.stop(), loop)

    # Optionally wait for thread to die (short timeout to avoid blocking)
    if loop_thread is not None and loop_thread.is_alive():
        loop_thread.join(timeout=1.0)

    with session_lock:
        main = None
        loop = None
        loop_thread = None

    logger.info("Gemini session stopped and reset")
    return Response(status=200)


@socketio.on("/robot/gemini/speak")
@app.route("/robot/gemini/speak", methods=["POST"])
@log("/robot/gemini/speak")
def speak_to_gemini():
    """
    The input PCM data (e.g. 16 kHz mono int16 from Pepper mic or another source)
    is streamed to Gemini Live. The generated output is then played on Pepper.
    """
    global main, loop

    # Only accept input if a session is active
    with session_lock:
        if main is None or loop is None or loop.is_closed():
            logger.warning("speak_to_gemini called but no active Gemini session")
            return Response("Gemini session not started", status=400)

    pcm_bytes = request.get_data()
    if not pcm_bytes:
        return Response("Empty audio payload", status=400)

    # Enqueue audio for Gemini on its event loop
    try:
        # schedule on async loop
        fut = asyncio.run_coroutine_threadsafe(main.enqueue_audio(pcm_bytes), loop)

        # get the real exception from inside the coroutine
        fut.result(timeout=1.0)

    except Exception as e:
        logger.error("Error enqueuing audio for Gemini: %s", e)
        logger.error("Full exception:", exc_info=True)
        return Response(f"Error sending audio to Gemini: {e}", status=500)

    return Response(status=200)


@socketio.on("/robot/gemini/set_api_key")
@app.route("/robot/gemini/set_api_key", methods=["POST"])
@log("/robot/gemini/set_api_key")
def set_gemini_api_key():
    """
    Updates the Gemini API key and reinitializes the client.

    Body JSON: {"api_key": "NEW_KEY"}
    """
    global client, loop_thread, main, loop

    data = request.get_json(silent=True) or {}
    new_key = data.get("api_key")

    if not new_key:
        return Response("Missing 'api_key' in JSON", status=400)

    with session_lock:
        # Prevent change while session is active
        if loop_thread is not None and loop_thread.is_alive():
            logger.warning("Attempt to change API key while session active.")
            return Response(
                "Cannot change API key while Gemini session is running.",
                status=409,
            )

        try:
            client = genai.Client(
                http_options={"api_version": "v1beta"},
                api_key=new_key,
            )
            logger.info("Gemini API key updated.")
        except Exception:
            logger.exception("Error updating Gemini client.")
            return Response("Failed to update Gemini API key", status=500)

    return Response(status=200)
