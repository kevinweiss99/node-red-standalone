import logging
import traceback
import sys
from flask import Flask
from flask_socketio import SocketIO
from flask_mqtt import Mqtt
from werkzeug.exceptions import HTTPException
import requests

from .config import MQTT_IP, MQTT_PORT

app = Flask(__name__)
app.config["SECRET_KEY"] = "Never Gonna Give You Up"
app.config["MQTT_BROKER_URL"] = MQTT_IP
app.config["MQTT_BROKER_PORT"] = MQTT_PORT
app.config["MQTT_CLIENT_ID"] = "Flask-server"
app.config["DEBUG"] = True

# cors header needed for esp connection
socketio = SocketIO(app, cors_allowed_origins="*")

# configure requests
request_session = requests.Session()
adapter = requests.adapters.HTTPAdapter(pool_connections=1, pool_maxsize=1)
request_session.mount('http://', adapter)
request_session.mount('https://', adapter)

logger = logging.getLogger(__name__)

try:
    logging.getLogger("flask_mqtt").setLevel(logging.ERROR)
    mqtt = Mqtt(app)
    
    logger.info("Connected to MQTT server {}:{}.".format(MQTT_IP, MQTT_PORT))
    mqtt.subscribe("internal/wrapper")
    mqtt.subscribe("esp/thermal/data")
    mqtt.subscribe("esp/connected")
    mqtt.subscribe("log")
    mqtt.subscribe("reset/awareness")
except ConnectionRefusedError as e:
    logger.error("Could not connect to MQTT server {}:{}.".format(MQTT_IP, MQTT_PORT))


@app.errorhandler(Exception)
def unhandled_exception(e):
    if isinstance(e, HTTPException):
        return e

    logger.critical(traceback.format_exc())
    return "Unhandled exception: See log for more info", 500
