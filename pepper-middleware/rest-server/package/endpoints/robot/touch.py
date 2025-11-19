import logging
import threading
import traceback

from flask import request, Response

from ...pepper.connection import awareness, motion
from ...config import DEFAULT_BASIC_AWARENESS_TRACKING, EASTER_EGGS
from ...decorator import log
from ...endpoints.robot.tablet import show_default_image
from ...endpoints.robot.tts import say
from ...mqtt import socketio_wrapper
from ...pepper.event_helper import pepper_event_publisher
from ...pepper.event_subscriber import Subscriber
from ...pepper.event_enum import PepperEvents
from ...server import app, socketio, mqtt

logger = logging.getLogger(__name__)

@socketio.on("/robot/wait/button")
@app.route("/robot/wait/button", methods=["POST"])
@log("/robot/wait/button")
def start_touch_detection(buttons: list[str] = None):
    try:
        if not buttons:
            buttons = request.get_json(force=True, silent=True)["buttons"]

        if pepper_event_publisher:
            on_touch_subscriber.buttons = buttons
            pepper_event_publisher.subscribe(on_touch_subscriber)

            return Response(status=200)
        else:
            logger.warning("Can't subscribe to touch detection event. Subscriber is not intialized.")
            return Response("Can't subscribe to touch detection event. Subscriber is not intialized.", status=500)

    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())

        return Response(str(e), status=400)


def external_move_reset(event, data):
    for sensor in data:
        if sensor[1]: # was sensor pressed?
            if "Base" in sensor[0]: # if the robot moved unexpectedly (i.e. manually moved) this sensor will be triggered and reset everything
                data = '{"topic": "reset/awareness", "payload": ""}'
                mqtt.publish("reset/awareness", data)

                if EASTER_EGGS and motion.robotIsWakeUp():
                    say(["Bitte nicht schubsen! Ich habe Joghurt im Rucksack.", "German", False])


def reset_awareness():
    awareness.setTrackingMode(DEFAULT_BASIC_AWARENESS_TRACKING)
    show_default_image()


@mqtt.on_topic("reset/awareness")
def qi_bridge_reset_awareness(client, userdata, message): # needed because we can't start a timer in a thread in the context of a qi module callback
    logger.info("Robot was forcefully moved. Resetting awareness state in 5 seconds.")
    timer = threading.Timer(5, reset_awareness)
    timer.start()


def on_touch_changed(event, data):
    head_touched = False
    button_word_list = " ".join(on_touch_subscriber.buttons)
    for sensor in data:
        if sensor[1]: # was sensor pressed?
            if "Head" in sensor[0]: # head sensor has multiple regions (i.e. Head/Touch/Front, ..Rear, ..Middle), but we don't care about that 
                head_touched = True
                
            if sensor[0] in button_word_list: # TODO TEST IT
                if head_touched:
                    socketio_wrapper("event/touched", "Head")
                else:
                    socketio_wrapper("event/touched", sensor[0])

                if pepper_event_publisher:
                    pepper_event_publisher.unsubscribe(on_touch_subscriber)

                on_touch_subscriber.buttons = []
                break


on_touch_subscriber = Subscriber(PepperEvents.TOUCH_CHANGED.value, on_touch_changed)
on_external_move_subscriber = Subscriber(PepperEvents.TOUCH_CHANGED.value, external_move_reset)

if pepper_event_publisher is not None:
    pepper_event_publisher.subscribe(on_external_move_subscriber)
