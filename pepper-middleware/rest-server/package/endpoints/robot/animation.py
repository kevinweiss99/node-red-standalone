import logging
import json

from flask import request, Response

from ...server import app, socketio
from ...pepper.connection import animation, posture, behavior, connection_type, ConnectionType
from ...decorator import log
from ...mqtt import socketio_wrapper
from .behavior import start_behavior
from ...config import BEHAVIOR_PREFIX

logger = logging.getLogger(__name__)

@socketio.on("/robot/animation/run")
@app.route("/robot/animation/run", methods=["POST"])
@log("/robot/animation/run")
def run_animation(animation_name = None):
    if not animation_name:
        animation_name = request.get_json(force=True, silent=True)["animation"]
    
    if animation_name.startswith(BEHAVIOR_PREFIX):
        return run_behavior(animation_name)
    
    return start_animation(animation_name)

@socketio.on("/robot/animations/validate")
@app.route("/robot/animations/validate", methods=["POST"])
@log("/robot/animations/validate")
def validate_animations(animations = None):
    if not animations:
        animations = request.get_json(force=True, silent=True)["animations"]
    
    if connection_type != ConnectionType.REAL_ROBOT:
        logger.info("Did not verify animations because the connection type is " + str(connection_type))
        return Response(json.dumps([]), status=200)

    valid_animations = animation._getAnimations() + behavior.getInstalledBehaviors()
    invalid = list(set(animations) - set(valid_animations))

    if len(invalid) > 0:
        logger.warning("The following animations are invalid: " + json.dumps(invalid))

    return Response(json.dumps(invalid), status=200)

def start_animation(animation_name):
    try:
        animation_future = animation.run(animation_name, _async=True)
        animation_future.addCallback(animation_finished)

        return Response(status=200)
    except Exception as e:
        logger.error(e)
        return Response(str(e), status=400)

def run_behavior(animation_name):
    if start_behavior(animation_name):
        return Response(status=200)
    else:
        return Response(status=400)

def animation_finished(animation_future):
    logger.debug("Animation finished")  

    try:
        posture_future = posture.goToPosture("Stand", 0.5, _async=True)
        posture_future.addCallback(posture_finished)
    except Exception as e:
        logger.error(e)

def posture_finished(posture_future):
    logger.debug("Posture finished")
    socketio_wrapper("/event/animation/finished")
