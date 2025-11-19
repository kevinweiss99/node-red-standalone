import logging
import traceback
import random
import qi
import time
import functools

from flask import request, Response

from .tts import speech_recognition_say
from ...decorator import log
from ...mqtt import socketio_wrapper
from ...pepper.connection import speech_recognition
from ...pepper.event_subscriber import Subscriber
from ...pepper.event_helper import pepper_event_publisher
from ...pepper.event_enum import PepperEvents
from ...server import app, socketio

logger = logging.getLogger(__name__)
random.seed()
speech_threshold = 1
detection_failed_inquires = []
language = ""
speech_recognition_paused = False

@socketio.on("/robot/speech-recognition/start")
@app.route("/robot/speech-recognition/start", methods=["POST"])
@log("/robot/speech-recognition/start")
def start_speech_recognition(data = None):
    global detection_failed_inquires
    global language

    try:
        if data:
            word, detection_failed_inquires, language, threshold = data
        else:
            word = request.get_json(force=True, silent=True)["word"]
            detection_failed_inquires = request.get_json(force=True, silent=True)["detectionFailedInquires"]
            language = request.get_json(force=True, silent=True)["language"]
            threshold = request.get_json(force=True, silent=True)["threshold"]

        global speech_threshold
        speech_threshold = float(threshold)

        speech_recognition.pause(True)

        start_speech_recognition_service(language, word)

        return Response(status=200)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())

        return Response(str(e), status=400)

@socketio.on("/robot/speech-recognition/stop")
@app.route("/robot/speech-recognition/stop", methods=["POST"])
@log("/robot/speech-recognition/stop")
def stop_speech_recognition():
    try:
        speech_recognition.pause(True)

        if pepper_event_publisher:
            pepper_event_publisher.unsubscribe(word_recognized_subscriber)

        return Response(status=200)
    except Exception as e:
        logger.debug(e)
        return Response(str(e), status=400)
    
def start_speech_recognition_service(language, word):
        # I'm not proud of this
        # fix to prevent "A grammar named "modifiable_grammar" already exists."
        speech_recognition.setLanguage("German")
        speech_recognition.setLanguage("English")

        speech_recognition.setLanguage(language)
        speech_recognition.setVocabulary(word, False)
        speech_recognition.setAudioExpression(True)
        speech_recognition.setVisualExpression(True)

        if pepper_event_publisher:
            pepper_event_publisher.subscribe(word_recognized_subscriber)
        else:
            logger.warning("Can't subscribe to speech recognition event. Publisher is not intialized.")

        speech_recognition.pause(False)

def on_word_recognized(event, data):
    global speech_threshold
    global detection_failed_inquires
    global speech_recognition_paused

    detection_successful = False
    expected_utterance = data[0]
    recognition_confidence = data[1]

    if recognition_confidence > speech_threshold:
        detection_successful = True
        stop_speech_recognition()

        socketio_wrapper("/event/speech/recognized", expected_utterance)

    if len(detection_failed_inquires) > 0 and not detection_successful and not speech_recognition_paused:
        speech_recognition.pause(True)
        speech_recognition_paused = True
        index = random.randint(0, len(detection_failed_inquires) - 1)
        speech_recognition_say([detection_failed_inquires[index], language], resume_speech_recognition)

def resume_speech_recognition(future):
    global speech_recognition_paused

    if future.hasError():
        logger.error("Error occurred while speech recognition was stopped.")

    speech_recognition.pause(False)
    speech_recognition_paused = False

word_recognized_subscriber = Subscriber(PepperEvents.WORD_RECOGNIZED.value, on_word_recognized)
