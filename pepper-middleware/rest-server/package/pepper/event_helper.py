import logging
import threading

from .connection import memory, session
from ..mqtt import socketio_wrapper
from ..pepper.event_publisher import Publisher
from ..pepper.event_subscriber import Subscriber
from ..pepper.event_enum import PepperEvents

logger = logging.getLogger(__name__)
pepper_event_publisher = None

def send_event(name, value = None):
    memory.declareEvent(name)
    memory.raiseEvent(name, value)

def on_battery_charge_changed(event, data):
    logger.info("Battery charge update: " + str(data))
    socketio_wrapper("/update/BatteryChargeChanged", str(data))

if session:
    pepper_event_publisher = Publisher()
    session.registerService(pepper_event_publisher.__class__.__name__, pepper_event_publisher)

    on_battery_subscriber = Subscriber(PepperEvents.BATTERY_CHARGE_CHANGED.value, on_battery_charge_changed)

    pepper_event_publisher.subscribe(on_battery_subscriber)
else:
    logger.warning("Didn't create PubSub event objects due to missing robot connection.")
