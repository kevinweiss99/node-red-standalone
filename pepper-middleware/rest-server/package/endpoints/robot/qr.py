import logging
import json

from flask import request, Response
from distutils.util import strtobool

from .awareness import _set_awareness
from ...config import CAMERA_UPDATE_INTERVAL
from ...decorator import log
from ...mqtt import socketio_wrapper
from ...pepper.connection import barcode
from ...pepper.event_helper import pepper_event_publisher
from ...pepper.event_subscriber import Subscriber
from ...pepper.event_enum import PepperEvents
from ...server import app, socketio

logger = logging.getLogger(__name__)
all_input = False


@socketio.on("/robot/qr/start")
@app.route("/robot/qr/start", methods=["POST"])
@log("/robot/qr/start")
def start_qr_detection(allow_all_input=None):
    if not allow_all_input:
        allow_all_input = request.get_json(force=True, silent=True)["allow_all_input"]

    global all_input
    all_input = strtobool(allow_all_input)

    _set_awareness(False)
    barcode.setActiveCamera(0) # Head camera
    barcode.setResolution(2) # 640x480
    barcode.setFrameRate(1000 / CAMERA_UPDATE_INTERVAL)

    barcode.subscribe("barcode_detection", 100, 0)

    if pepper_event_publisher:
        pepper_event_publisher.subscribe(qr_detected_subscriber)
    else:
        logger.warning("Can't subscribe to qr detection event. Subscriber is not intialized.")

    return Response(status=200)

@socketio.on("/robot/qr/stop")
@app.route("/robot/qr/stop", methods=["POST"])
@log("/robot/qr/stop")
def stop_qr_detection():
    try:
        _set_awareness(True)
        barcode.unsubscribe("barcode_detection", _async=True)

        if pepper_event_publisher:
            pepper_event_publisher.unsubscribe(qr_detected_subscriber)

        return Response(status=200)
    except Exception as e:
        logger.warning(e)
        return Response(str(e), status=400)

def on_qr_code_deteced(event, data):
    global all_input

    try:
        stop = False

        for qr in data:
            qr = qr[0] # get only the value of the qr, [1] is an int array - perhaps the location
            if "id" in qr:
                qr_json = json.loads(qr)
                socketio_wrapper("/event/qr/detected", qr_json["id"])
                stop = True
                break
            else:
                if all_input:
                    socketio_wrapper("/event/qr/detected", qr)
                    stop = True
                    break
                else:
                   logger.info("Wrong QR-Code format detected")
                
        if stop:
            stop_qr_detection()
    except Exception as e:
        logger.error(e)

qr_detected_subscriber = Subscriber(PepperEvents.QR_DETECTED.value, on_qr_code_deteced)