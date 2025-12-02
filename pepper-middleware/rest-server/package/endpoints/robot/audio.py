from flask import request, Response
import logging

from ...server import app, socketio
from ...pepper.connection import audio
from ...decorator import log

logger = logging.getLogger(__name__)

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

    logger.warning("Received message number %s", frame_number)

    # Optionally: sanity check the size
    if len(buffer) > 16384:
        return Response("Buffer too large", status=400)

    audio.sendRemoteBufferToOutput(nbOfFrames, buffer, _async=True)
    return Response("", status=200)


@app.route("/robot/output/setBufferWithConvert", methods=["POST"])
@log("/robot/output/setBufferWithConvert")
def setBufferWithConver():
    """
    Expects 48 kHz PCM 16-bit stereo interleaved audio data of any size as raw body.
    """
    stereo_48k_pcm = request.get_data()  # raw bytes from request body
    frame_number = int(request.args["messageNumber"])

    logger.warning("Received message number %s", frame_number)

    # Each stereo frame is 4 bytes (2 channels × 2 bytes)
    MAX_PEPPER_BUFFER_BYTES = 16384
    for offset in range(0, len(stereo_48k_pcm), MAX_PEPPER_BUFFER_BYTES):
        chunk = stereo_48k_pcm[offset:offset + MAX_PEPPER_BUFFER_BYTES]
        if not chunk:
            continue
        nb_frames = len(chunk) // 4
        if nb_frames <= 0:
            continue
        
        audio.sendRemoteBufferToOutput(nb_frames, chunk, _async=True)
    
    return Response("", status=200)
