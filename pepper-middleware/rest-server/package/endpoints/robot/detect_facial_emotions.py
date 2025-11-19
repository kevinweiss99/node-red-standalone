import logging
import traceback

from flask import Response
from flask_socketio import emit

from ...server import app, socketio
from ...pepper.connection import face_detection
from ...config import CAMERA_UPDATE_INTERVAL
from ...decorator import log
from .awareness import _set_awareness

logger = logging.getLogger(__name__)

@socketio.on("/robot/face/start")
@app.route("/robot/face/start", methods=["POST"])
@log("/robot/face/start")
def start_face_detection():
    try:
        _set_awareness(False, pitch=-20)

        face_detection.setRecognitionEnabled(False)
        face_detection.subscribe("face_detection", CAMERA_UPDATE_INTERVAL, 0)

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

        return Response(status=200)
    except Exception as e:
        logger.warning(e)
        return Response(str(e), status=400)

def on_face_detected(faces):
    faces = faces[0]

    if len(faces) == 0:
        return

    data = []
    for i in range(len(faces[1]) - 1):
        data.append(faces[1][i][0][1:])
    
    # [FACES[x, y, size_x, size_y]]
    face_count = len(data)
    stop_face_detection()

    emit("/event/face/detected", face_count, broadcast=True, namespace="/")
