from flask import request, Response
import os
import logging
import traceback

from ...server import app, socketio
from ...pepper.connection import audio_player
from ...decorator import log

logger = logging.getLogger(__name__)


@app.route("/robot/audio_player", methods=["GET"])
@log("/robot/audio_player")
def play_existing_file():
    """
    Example: GET /robot/audio_player?filename=attention.wav
    Plays /home/nao/attention.wav
    """
    filename = request.args.get("filename")
    if not filename:
        return Response("Missing 'filename' query parameter", status=400)

    try:
        audio_player.playFile(f"/home/nao/{filename}")
    except Exception as e:
        return Response(str(e), status=500)

    return Response(status=200)