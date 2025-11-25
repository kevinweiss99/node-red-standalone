from flask import request, Response
import logging

from ...server import app, socketio
from ...pepper.connection import audio_player
from ...decorator import log

logger = logging.getLogger(__name__)


def _get_volume_from_query(default=1.0):
    """Parse ?volume=... as float in [0.0, 1.0]."""
    raw = request.args.get("volume", None)
    if raw is None:
        return float(default)
    try:
        vol = float(raw)
    except ValueError:
        return float(default)
    # clamp to [0.0, 1.0]
    if vol < 0.0:
        vol = 0.0
    if vol > 1.0:
        vol = 1.0
    return vol


@app.route("/robot/audio_player/playfile", methods=["GET"])
@log("/robot/audio_player/playfile")
def play_existing_file():
    """
    Example: GET /robot/audio_player/playfile?filename=attention.wav&volume=0.8
    Plays /home/nao/attention.wav asynchronously.
    """
    filename = request.args.get("filename")
    if not filename:
        return Response("Missing 'filename' query parameter", status=400)

    volume = _get_volume_from_query(default=1.0)

    try:
        # playFile(fileName, volume, pan)
        audio_player.playFile(f"/home/nao/{filename}", volume, 0.0, _async=True)
    except Exception as e:
        return Response(str(e), status=500)

    return Response(status=200)


@app.route("/robot/audio_player/webstream", methods=["GET"])
@log("/robot/audio_player/webstream")
def play_webstream():
    """
    Example: GET /robot/audio_player/webstream?url=http://...&volume=0.8
    Plays mp3 web radio / web file asynchronously.
    """
    url = request.args.get("url")
    if not url:
        return Response("Missing 'url' query parameter", status=400)

    volume = _get_volume_from_query(default=1.0)

    try:
        # playWebStream(streamName, volume, pan)
        audio_player.playWebStream(url, volume, 0.0, _async=True)
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
