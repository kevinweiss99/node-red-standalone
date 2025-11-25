from flask import request, Response
import os
import logging
import traceback

from ...server import app, socketio
from ...pepper.connection import audio_player
from ...decorator import log

logger = logging.getLogger(__name__)

AUDIO_DIR = "/home/nao"


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

    path = os.path.join(AUDIO_DIR, filename)

    if not os.path.isfile(path):
        return Response("File not found: " + path, status=404)

    try:
        audio_player.playFile(path)
    except Exception as e:
        return Response(str(e), status=500)

    return Response(status=200)


@app.route("/robot/audio_player", methods=["POST"])
@log("/robot/audio_player")
def upload_file():
    """
    Expects multipart/form-data with a part named "file".
    Saves it to /home/nao/<filename>.
    """
    if "file" not in request.files:
        return Response("No file part named 'file' in request", status=400)

    f = request.files["file"]
    if f.filename == "":
        return Response("Empty filename", status=400)

    ext = os.path.splitext(f.filename)[1].lower()

    save_path = os.path.join(AUDIO_DIR, f.filename)

    try:
        f.save(save_path)
        return Response(str(save_path), status=200)
    except Exception as e:
        return Response(str(e), status=500)
