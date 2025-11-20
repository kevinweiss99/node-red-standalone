import logging
import traceback
import cv2
import numpy as np
from flask import Response, stream_with_context
from ...pepper.connection import video
from ...server import app, socketio

logger = logging.getLogger(__name__)

CAMERA_ID = 0   # 0 = Top Camera, 1 = Bottom Camera
RESOLUTION = 2  # 2 = 640x480
COLORSPACE = 11 # RGB
FPS = 10

def generate():
    nameId = video.subscribeCamera("mjpeg_stream", CAMERA_ID, RESOLUTION, COLORSPACE, FPS)
    while True:

        frame = video.getImageRemote(nameId)
        if not frame:
            continue

        width, height = frame[0], frame[1]
        data = frame[6]

        img = np.frombuffer(data, dtype=np.uint8).reshape(height, width, 3)
        ret, jpeg = cv2.imencode(".jpg", img)
        if not ret:
            continue

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" +
            jpeg.tobytes() +
            b"\r\n"
        )

@app.route("/robot/camera/stream")
def stream():
    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")
