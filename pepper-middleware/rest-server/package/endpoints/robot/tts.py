import logging

from flask import request, Response

from ...server import app, socketio
from ...pepper.connection import tts, speaking_movement, tts_animated
from ...decorator import log
from ...mqtt import socketio_wrapper

logger = logging.getLogger(__name__)

@socketio.on("/robot/tts/say")
@app.route("/robot/tts/say", methods=["POST"])
@log("/robot/tts/say")
def say(data = None):
    try:
        if data:
            text, language, is_animated = data
        else:
            text = request.get_json(force=True, silent=True)["text"]
            language = request.get_json(force=True, silent=True)["language"]
            is_animated = request.get_json(force=True, silent=True)["isAnimated"]
        
        tts.setLanguage(language)

        future = None

        if is_animated:
            future = tts_animated.say(str(text), _async=True)
        else:
            future = tts.say(str(text), _async=True)

        future.addCallback(tts_finished)
        return Response(status=200)
    except Exception as e:
        logger.error(e)
        return Response(str(e), status=400)

@socketio.on("/robot/tts/volume")
@app.route("/robot/tts/volume", methods=["POST"])
@log("/robot/tts/volume")
def set_tts_volume(volume = None):
    if not volume:
        volume = request.get_json(force=True, silent=True)["volume"]
    
    tts.setVolume(volume)

    return Response(status=200)

@app.route("/robot/tts/volume")
@log("/robot/tts/volume")
def get_tts_volume():
    return Response(str(_get_tts_volume()), status=200)

def _get_tts_volume():
    tts_volume = tts.getVolume()
    
    if not tts_volume:
        tts_volume = "-"

    return tts_volume

def speech_recognition_say(data, callback):
    try:
        if data:
            text, language = data
        else:
            text = request.get_json(force=True, silent=True)["text"]
            language = request.get_json(force=True, silent=True)["language"]

        tts.setLanguage(language)
        future = tts.say(str(text), _async=True)
        future.addCallback(callback)

        return Response(status=200)
    except Exception as e:
        logger.error(e)
        return Response(str(e), status=400)

def tts_finished(future):
    logger.debug("TTS finished")

    # reset language to german
    tts.setLanguage("German")

    socketio_wrapper("/event/tts/finished")


speaking_movement.setMode("contextual")
speaking_movement.setEnabled(True)