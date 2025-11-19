import logging
import traceback

from flask import Response

from .awareness import _set_awareness
from ...config import CAMERA_UPDATE_INTERVAL
from ...decorator import log
from ...mqtt import socketio_wrapper
from ...pepper.connection import face_detection
from ...pepper.event_subscriber import Subscriber
from ...pepper.event_helper import pepper_event_publisher
from ...pepper.event_enum import PepperEvents
from ...server import app, socketio

logger = logging.getLogger(__name__)

@socketio.on("/robot/face/start")
@app.route("/robot/face/start", methods=["POST"])
@log("/robot/face/start")
def start_face_detection():
    try:
        _set_awareness(False, pitch=-20)

        face_detection.setRecognitionEnabled(False)
        face_detection.subscribe("face_detection", CAMERA_UPDATE_INTERVAL, 0)

        if pepper_event_publisher:
            pepper_event_publisher.subscribe(face_detected_subscriber)
        else:
            logger.warning("Can't subscribe to face detection event. Subscriber is not intialized.")

        return Response(status=200)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return Response(str(e), status=500)

@socketio.on("/robot/face/stop")
@app.route("/robot/face/stop", methods=["POST"])
@log("/robot/face/stop")
def stop_face_detection():
    try:
        _set_awareness(True)
        face_detection.unsubscribe("face_detection", _async=True)

        if pepper_event_publisher:
            pepper_event_publisher.unsubscribe(face_detected_subscriber)

        return Response(status=200)
    except Exception as e:
        logger.warning(e)
        return Response(str(e), status=400)

def on_face_detected(event, value):
    faces = value

    if len(faces) == 0:
        return

    data = []
    for i in range(len(faces[1]) - 1):
        data.append(faces[1][i][0][1:])
    
    # [FACES[x, y, size_x, size_y]]
    face_count = len(data)
    stop_face_detection()

    socketio_wrapper("/event/face/detected", face_count)

face_detected_subscriber = Subscriber(PepperEvents.FACE_DETECTED.value, on_face_detected)