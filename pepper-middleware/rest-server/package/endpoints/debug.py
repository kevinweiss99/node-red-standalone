import logging

from sys import flags
from flask import render_template

from ..server import app, socketio
from ..config import FLASK_IP, FLASK_PORT, EASTER_EGGS
from ..pepper.connection import connection_type, memory
from .robot.battery import _get_battery_percentage
from .robot.temperature import _get_temperature
from .robot.audio import _get_general_volume
from .robot.system import _get_name
from .robot.tts import _get_tts_volume
from .esp.esp import get_connection_status
from .esp.thermal_camera import get_camera_status

logger = logging.getLogger(__name__)

@app.route("/", methods=["GET"])
def get_debug_page():
    battery_percentage = _get_battery_percentage()
    temperature = _get_temperature()
    general_volume = _get_general_volume()
    tts_volume = _get_tts_volume()
    robot_name = _get_name()

    try:
        tts_volume = int(float(tts_volume) * 100)
    except (ValueError, TypeError):
        if type(tts_volume) == "Dummy":
            tts_volume = "-"

    if type(battery_percentage) == "Dummy":
        battery_percentage = "-"
    if type(temperature) == "Dummy":
        temperature = "-"
    if type(general_volume) == "Dummy":
        general_volume = 0
    
    return render_template("index.html",
        robot_name = robot_name,
        flask_ip = "{}:{}".format(FLASK_IP, FLASK_PORT),
        connection_type=connection_type,
        battery=battery_percentage,
        temperature=temperature,
        general_volume=general_volume,
        tts_volume=tts_volume,
        esp_connection = "connected" if get_connection_status() else "disconnected",
        camera_status=get_camera_status(),
        easter_eggs=EASTER_EGGS)

@socketio.on("/site/debug")
def debug_button():
    pass