import logging
import json

from flask_socketio import emit

from .server import mqtt, app
from .config import MQTT_IP

logger = logging.getLogger(__name__)

@mqtt.on_connect()
def on_mqtt_connect(client, userdata, flags, rc):
    logger.warning("Something weird happened.")

@mqtt.on_disconnect()
def on_mqtt_disconnect_message():
    logger.warning("Disconnected from MQTT server {}.".format(MQTT_IP))

@mqtt.on_message()
def on_mqtt_message(client, userdata, message):
    logger.warning("Unknown topic {} received.".format(message.topic))

def socketio_wrapper(socketio_topic, payload = ""):
    data = {"topic": socketio_topic, "payload": payload}

    mqtt.publish("internal/wrapper", json.dumps(data))

@mqtt.on_topic("internal/wrapper")
def socketio_wrapper_receiver(client, userdata, message):
    try:
        data = json.loads(message.payload.decode())

        with app.test_request_context():
            emit(data["topic"], data["payload"], broadcast=True, namespace="/")
    except Exception as e:
        logger.error(e)
