import logging
import ast

from flask_socketio import emit

from ...server import app
from ...mqtt import mqtt
from ...decorator import log

esp_connected = False

logger = logging.getLogger(__name__)

@mqtt.on_topic("esp/connected")
@log("/esp/connected")
def handle_esp_connection_status(client, userdata, message):
    payload = message.payload.decode()

    try:
        global esp_connected
        esp_connected = ast.literal_eval(payload)
    except ValueError:
        logger.warning("\"{}\" is not a valid boolean.".format(payload))
        return

    esp_connection = "connected" if esp_connected else "disconnected"

    with app.test_request_context():
        emit("/update/esp_connection", esp_connection, broadcast=True, namespace="/")

def get_connection_status():
    global esp_connected
    return esp_connected
