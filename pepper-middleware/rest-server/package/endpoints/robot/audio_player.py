from flask import request, Response
import os
import logging
import traceback

from ...server import app, socketio
from ...pepper.connection import audio_player
from ...decorator import log

logger = logging.getLogger(__name__)


@app.route("/robot/audio_player/playfile", methods=["GET"])
@log("/robot/audio_player/playfile")
def play_existing_file():
    """
    Example: GET /robot/audio_player/playfile?filename=attention.wav
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

@app.route("/robot/audio_player/playfile/async", methods=["GET"])
@log("/robot/audio_player/playfile/async")
def play_existing_file_async():
    """
    Example: GET /robot/audio_player/playfile/async?filename=attention.wav
    Plays /home/nao/attention.wav
    """
    filename = request.args.get("filename")
    if not filename:
        return Response("Missing 'filename' query parameter", status=400)

    try:
        audio_player.playFile(f"/home/nao/{filename}", _async=True)
    except Exception as e:
        return Response(str(e), status=500)
    return Response(status=200)

@app.route("/robot/audio_player/play", methods=["GET"])
@log("/robot/audio_player/play")
def play_existing_file_alt():
    """
    Example: GET /robot/audio_player/play?filename=attention.wav
    Plays /home/nao/attention.wav
    """
    filename = request.args.get("filename")
    if not filename:
        return Response("Missing 'filename' query parameter", status=400)

    try:
        fileId = audio_player.loadFile(f"/home/nao/{filename}")
        audio_player.play(fileId)
    except Exception as e:
        return Response(str(e), status=500)
    return Response(status=200)

@app.route("/robot/audio_player/play/async", methods=["GET"])
@log("/robot/audio_player/play/async")
def play_existing_file_alt_async():
    """
    Example: GET /robot/audio_player/play/async?filename=attention.wav
    Plays /home/nao/attention.wav
    """
    filename = request.args.get("filename")
    if not filename:
        return Response("Missing 'filename' query parameter", status=400)

    try:
        fileId = audio_player.loadFile(f"/home/nao/{filename}")
        audio_player.play(fileId, _async=True)
    except Exception as e:
        return Response(str(e), status=500)
    return Response(status=200)

@app.route("/robot/audio_player/webstream", methods=["GET"])
@log("/robot/audio_player/webstream")
def play_webstream():
    """
    Example: GET /robot/audio_player/webstream?url=http://stream.antennethueringen.de/live/aac-64/stream.antennethueringen.de/
    Plays the web radio
    """
    url = request.args.get("url")
    if not url:
        return Response("Missing 'url' query parameter", status=400)

    try:
        audio_player.playWebStream(url, 1.0, 0.0)
    except Exception as e:
        return Response(str(e), status=500)
    return Response(status=200)

@app.route("/robot/audio_player/webstream/async", methods=["GET"])
@log("/robot/audio_player/webstream/async")
def play_webstream_async():
    """
    Example: GET /robot/audio_player/webstream/async?url=http://stream.antennethueringen.de/live/aac-64/stream.antennethueringen.de/
    Plays the web radio
    """
    url = request.args.get("url")
    if not url:
        return Response("Missing 'url' query parameter", status=400)

    try:
        audio_player.playWebStream(url, 1.0, 0.0, _async=True)
    except Exception as e:
        return Response(str(e), status=500)
    return Response(status=200)

@app.route("/robot/audio_player/stop", methods=["GET"])
@log("/robot/audio_player/stop")
def stop_playback():
    try:
        audio_player.stopAll()
    except Exception as e:
        return Response(str(e), status=500)
    return Response(status=200)