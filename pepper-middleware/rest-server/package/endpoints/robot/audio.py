from flask import request, Response
import logging
import threading
import queue
import time

from ...server import app, socketio
from ...pepper.connection import audio
from ...decorator import log

logger = logging.getLogger(__name__)

# ---- Simple playback queue ----
BUFFER_QUEUE = queue.Queue()
PLAYBACK_DELAY = 0.02  # seconds between buffers; tweak as needed

def playback_worker():
    """
    Background worker that plays queued buffers in order with small delays.
    """
    next_item = None
    while True:
        nbOfFrames, buffer, frame_number = BUFFER_QUEUE.get()
        try:
            logger.debug(
                "Playing frame %d (queue size after get: %d)",
                frame_number,
                BUFFER_QUEUE.qsize()
            )
            # Use synchronous call to preserve ordering at this level
            audio.sendRemoteBufferToOutput(nbOfFrames, buffer, _async=False)
            time.sleep(PLAYBACK_DELAY)
        except Exception:
            logger.exception("Error while playing audio buffer frame %d", frame_number)
        finally:
            BUFFER_QUEUE.task_done()

# Start worker thread when module is imported
_worker_thread = threading.Thread(target=playback_worker, daemon=True)
_worker_thread.start()
# -------------------------------

@socketio.on("/robot/output/volume")
@app.route("/robot/output/volume", methods=["POST"])
@log("/robot/output/volume")
def set_general_volume(volume = None):
    if not volume:
        volume = request.get_json(force=True, silent=True)["volume"]

    volume = int(volume)

    if(0 < int(volume) < 1):
        logger.warning("The output volume has a range of 0 to 100.")
    
    volume = max(1, volume) # ensure volume is at least 1
    audio.setOutputVolume(int(volume))

    return Response(status=200)

@app.route("/robot/output/volume")
@log("/robot/output/volume")
def get_general_volume():
    return Response(str(_get_general_volume()), status=200)

def _get_general_volume():
    output_volume = audio.getOutputVolume()
    
    if not output_volume:
        output_volume = "-"

    return output_volume

@app.route("/robot/output/setBuffer", methods=["POST"])
@log("/robot/output/setBuffer")
def setBuffer():
    """
    Expects 48 kHz PCM 16-bit stereo interleaved audio data (<16 KB) as raw body.
    nbOfFrames is passed as query parameter.
    """
    nbOfFrames = int(request.args["nbOfFrames"])
    buffer = request.get_data()  # raw bytes from request body
    frame_number = int(request.args["messageNumber"])

    logger.warning("Received message number %d", frame_number)

    # Optionally: sanity check the size
    if len(buffer) > 16384:
        return Response("Buffer too large", status=400)

    audio.sendRemoteBufferToOutput(nbOfFrames, buffer, _async=True)

    return Response("", status=200)

@app.route("/robot/output/setBufferQueued", methods=["POST"])
@log("/robot/output/setBuffer")
def setBuffer():
    """
    Expects 48 kHz PCM 16-bit stereo interleaved audio data (<16 KB) as raw body.
    nbOfFrames is passed as query parameter.
    """
    nbOfFrames = int(request.args["nbOfFrames"])
    buffer = request.get_data()  # raw bytes from request body
    frame_number = int(request.args["messageNumber"])

    logger.warning("Received message number %d", frame_number)

    # Optionally: sanity check the size
    if len(buffer) > 16384:
        return Response("Buffer too large", status=400)

    # Enqueue buffer instead of sending directly
    BUFFER_QUEUE.put((nbOfFrames, buffer, frame_number))

    return Response("", status=200)
