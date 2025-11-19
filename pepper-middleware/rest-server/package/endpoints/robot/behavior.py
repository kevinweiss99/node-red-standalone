import logging

from ...pepper.connection import behavior, posture
from ...decorator import log
from ...mqtt import socketio_wrapper
from ...config import BEHAVIOR_PREFIX

logger = logging.getLogger(__name__)

def __get_custom_behaviors():
    behavior_list = behavior.getInstalledBehaviors()
    return [b for b in behavior_list if b.startswith(BEHAVIOR_PREFIX)]

def __preload_behavios():
    for b in __get_custom_behaviors():
        if not behavior.preloadBehavior(b):
            logger.warning("Could not preload behavior \"{}\".".format(b))

def start_behavior(name):
    if not behavior.isBehaviorInstalled(name):
        logger.error("The behavior \"{}\" is not installed.".format(name))
        return False
    
    try:
        behavior_future = behavior.runBehavior(name, _async=True)
        behavior_future.addCallback(behavior_finished)
        return True
    except Exception as e:
        logger.error(e)
        return False

def behavior_finished(behavior_future):
    logger.debug("Behavior finished")
    
    try:
        posture_future = posture.goToPosture("Stand", 0.5, _async=True)
        posture_future.addCallback(posture_finished)
    except Exception as e:
        logger.error(e)

def posture_finished(posture_future):
    logger.debug("Posture finished")
    socketio_wrapper("/event/animation/finished")

__preload_behavios()
