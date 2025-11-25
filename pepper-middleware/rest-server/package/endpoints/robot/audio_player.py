from flask import request, Response
import os
import uuid
import logging
import traceback

from ...server import app, socketio
from ...pepper.connection import audio_player
from ...decorator import log

logger = logging.getLogger(__name__)

@app.route("/robot/audio_player/attention", methods=["GET"])
@log("/robot/audio_player/attention")
def play_uploaded_file():
    try:
        audio_player.playFile("home/nao/attention.wav")
    except Exception as e:
        return Response(str(e), 400)        

    return Response(status=200)