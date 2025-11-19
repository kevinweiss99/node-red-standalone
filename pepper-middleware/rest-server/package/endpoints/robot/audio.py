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