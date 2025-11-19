import logging
import threading

from flask import jsonify, Response, request
from flask_socketio import emit

from ..server import app
from ..decorator import log
from ..config import SUBSCRIBED_SERVICES, EASTER_EGGS
from ..endpoints.robot.face_detection import on_face_detected
from ..endpoints.robot.qr import on_qr_code_deteced
from ..endpoints.robot.speech_recognition import on_word_recognized
from ..endpoints.robot.tts import say
from ..endpoints.robot.tablet import show_default_image
from ..pepper.connection import awareness, motion

logger = logging.getLogger(__name__)
config_called = False # set to true after robot updates event list

@app.route("/pepper/event", methods=["POST"])
@log("/pepper/event")
def pepper_event():
    service_name = request.json["service_name"]
    event = request.json["event"]
    data = request.json["data"]

    if event == "FaceDetected":
        on_face_detected(data)
    elif event == "BarcodeReader/BarcodeDetected":
        on_qr_code_deteced(data)
    elif event == "BatteryChargeChanged":
        emit("/update/BatteryChargeChanged", data[0], broadcast=True, namespace="/")
    elif event == "WordRecognized":
        on_word_recognized(data)
    elif event == "TouchChanged":
        head_touched = False

        for sensor in data[0]:
            if sensor[1]: #sensor pressed
                if "Head" in sensor[0]:
                    if head_touched:
                        break
                    
                    head_touched = True
                    emit("/event/Head", broadcast=True, namespace="/")
                else:
                    if "Base" in sensor[0]:
                        awareness_timer = threading.Timer(5, reset_awareness)
                        awareness_timer.start()

                        if EASTER_EGGS and motion.robotIsWakeUp():
                            say(["Bitte nicht schubsen! Ich habe Joghurt im Rucksack.", "German"])

                    emit("/event/" + sensor[0], broadcast=True, namespace="/")
    else:
        emit("/event/{}/{}".format(service_name, event), data, broadcast=True, namespace="/")

    return Response(status=200)

@app.route("/pepper/config")
@log("/pepper/config")
def pepper_config():
    global config_called
    config_called = True

    return jsonify(SUBSCRIBED_SERVICES)

def is_event_list_updated():
    global config_called

    if not config_called:
        logger.warning("Event list update failed - Python script on Pepper is not running.")

def reset_awareness():
    awareness.setTrackingMode("Head")
    show_default_image()

connection_timer = threading.Timer(3, is_event_list_updated)
connection_timer.start()
