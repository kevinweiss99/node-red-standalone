from flask import request, Response
import os
import uuid
import logging

from ...server import app, socketio
from ...pepper.connection import audio, audio_player  # audio = ALAudioDevice, audio_player = ALAudioPlayer
from ...decorator import log

logger = logging.getLogger(__name__)

@app.route("/robot/audio_player/attention", methods=["GET"])
@log("/robot/audio_player/attention")
def play_uploaded_file():
    audio_player.playFile("home/nao/attention.wav")

    return Response(status=200)