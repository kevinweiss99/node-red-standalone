import logging,traceback,cv2,numpy as np,base64
from threading import Thread,Event
from flask import Response
from ...pepper.connection import video
from ...server import app,socketio
import cv2
import mediapipe as mp

logger=logging.getLogger(__name__)
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=True,
    max_num_hands=2,
    model_complexity=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

CAMERA_ID=0
RESOLUTION=3
RES_LOW=1
COLORSPACE=11
FPS=5
stream_thread=None
stop_event=Event()

def is_index_finger_up(landmarks):
    tip = landmarks[8].y
    dip = landmarks[7].y
    pip = landmarks[6].y
    mcp = landmarks[5].y
    return tip < dip < pip < mcp 

@app.route("/robot/camera/snapshot")
def camera_snapshot():
    cam=None
    try:
        cam=video.subscribeCamera("snapshot_once",CAMERA_ID,RES_LOW,COLORSPACE,FPS)
        frame=video.getImageRemote(cam)
        if frame is None: return Response("Fail",status=500)
        w=frame[0];h=frame[1];data=frame[6]
        img=np.frombuffer(data,dtype=np.uint8).reshape((h,w,3))
        img=cv2.cvtColor(img,cv2.COLOR_RGB2BGR)
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)
        finger_up = False
        if result.multi_hand_landmarks:
            lm = result.multi_hand_landmarks[0].landmark
            finger_up = is_index_finger_up(lm)

        text = "Finger UP" if finger_up else "Finger DOWN"
        cv2.putText(img, text, (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

        ok, jpeg = cv2.imencode(".jpg", img)
        if not ok:
            return Response("Fail", status=500)
        return Response(f"{finger_up}", status=200)
        #return Response(jpeg.tobytes(), mimetype="image/jpeg", status=200)
    except Exception as e:
        logger.error(e)
        return Response(f"Camera error: {e}",status=500)
    finally:
        if cam: video.unsubscribe(cam)

@app.route("/robot/camera/object")
def get_came_obj():
    cid=video.subscribeCamera("mjpeg_stream",CAMERA_ID,RESOLUTION,COLORSPACE,FPS)
    return Response(str(cid),status=200)
