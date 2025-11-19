import math
import logging

from flask import request, Response

from ...config import DEFAULT_BASIC_AWARENESS_TRACKING
from ...server import app, socketio
from ...pepper.connection import motion, awareness
from .tablet import show_default_image
from ...decorator import log
from ...mqtt import socketio_wrapper

logger = logging.getLogger(__name__)

@socketio.on("/robot/motion/rest")
@app.route("/robot/motion/rest", methods=["POST"])
@log("/robot/motion/rest")
def rest():
    try:
        rest_future = motion.rest(_async=True)
        rest_future.addCallback(rest_finished)

        return Response(status=200)
    except Exception as e:
        logger.error(e)
        return Response(str(e), status=500)

@socketio.on("/robot/motion/wakeup")
@app.route("/robot/motion/wakeup", methods=["POST"])
@log("/robot/motion/wakeup")
def wake_up():
    try:
        wake_up_future = motion.wakeUp(_async=True)
        wake_up_future.addCallback(wake_up_finished)

        return Response(status=200)
    except Exception as e:
        logger.error(e)
        return Response(str(e), status=500)

@socketio.on("/robot/motion/head/pitch")
@app.route("/robot/motion/head/pitch", methods=["POST"])
@log("/robot/motion/head/pitch")
def set_head_pitch(angle = None):
    if angle is None:
        angle = request.get_json(force=True, silent=True)["angle"]

    motion.angleInterpolation("HeadPitch", math.radians(angle), 2, True, _async=True)

    return Response(status=200)

@socketio.on("/robot/motion/head/yaw")
@app.route("/robot/motion/head/yaw", methods=["POST"])
@log("/robot/motion/head/yaw")
def set_head_yaw(angle = None):
    if angle is None:
        angle = request.get_json(force=True, silent=True)["angle"]

    motion.angleInterpolation("HeadYaw", math.radians(angle), 2, True, _async=True)

    return Response(status=200)

@socketio.on("/robot/motion/hand/open")
@app.route("/robot/motion/hand/open", methods=["POST"])
@log("/robot/motion/hand/open")
def open_hand(hand = None):
    try:
        if hand is None:
            hand = request.get_json(force=True, silent=True)["hand"]

        open_future = motion.openHand(hand, _async=True)
        open_future.addCallback(open_finished)

        return Response(status=200)
    except Exception as e:
        logger.error(e)
        return Response(str(e), status=500)
    
@socketio.on("/robot/motion/hand/close")
@app.route("/robot/motion/hand/close", methods=["POST"])
@log("/robot/motion/hand/open")
def close_hand(hand = None):
    try:
        if hand is None:
            hand = request.get_json(force=True, silent=True)["hand"]

        close_future = motion.closeHand(hand, _async=True)
        close_future.addCallback(close_finished)
        
        return Response(status=200)
    except Exception as e:
        logger.error(e)
        return Response(str(e), status=500)
    
def open_finished(open_future):
    logger.debug("Hand opened")
    socketio_wrapper("/motion/hand/open/finished")

def close_finished(close_future):
    logger.debug("Hand closed")
    socketio_wrapper("/motion/hand/close/finished")

def rest_finished(rest_future):
    logger.debug("Rest postition reached")
    socketio_wrapper("/motion/rest/finished")

def wake_up_finished(wake_up_future):
    awareness.setTrackingMode(DEFAULT_BASIC_AWARENESS_TRACKING)
    show_default_image()

    logger.debug("Wake up position reached")
    socketio_wrapper("/motion/wakeup/finished")

# motion.setOrthogonalSecurityDistance(0.2)
# motion.setTangentialSecurityDistance(0.05)

# logger.debug(motion.getOrthogonalSecurityDistance())
# logger.debug(motion.getTangentialSecurityDistance())