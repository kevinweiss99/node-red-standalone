import logging

from flask import request, Response

from ...server import app, socketio
from ...pepper.connection import led
from ...decorator import log

logger = logging.getLogger(__name__)

@socketio.on("/robot/led/start")
@app.route("/robot/led/start", methods=["POST"])
@log("/robot/led/start")
def led_start(group = None):
    if not group:
        group = request.get_json(force=True, silent=True)["group"]

    try:
        led.on(group)
        return Response(status=200)
    except Exception as e:
        logger.error(e)
        return Response(status=500)

@socketio.on("/robot/led/stop")
@app.route("/robot/led/stop", methods=["POST"])
@log("/robot/led/stop")
def led_stop(group = None):
    if not group:
        group = request.get_json(force=True, silent=True)["group"]

    try:
        led.off(group)
        return Response(status=200)
    except Exception as e:
        logger.error(e)
        return Response(status=500)

@socketio.on("/robot/led/rasta")
@app.route("/robot/led/rasta", methods=["POST"])
@log("/robot/led/rasta")
def led_rasta(duration = None):
    if not duration:
        duration = request.get_json(force=True, silent=True)["duration"]

    try:
        led.rasta(duration)
        return Response(status=200)
    except Exception as e:
        logger.error(e)
        return Response(status=500)

@socketio.on("/robot/led/fade")
@app.route("/robot/led/fade", methods=["POST"])
@log("/robot/led/fade")
def led_fade(data = None):
    if data:
        group, color_name, duration = data
    else:
        group = request.get_json(force=True, silent=True)["group"]
        color_name = request.get_json(force=True, silent=True)["color_name"]
        duration = request.get_json(force=True, silent=True)["duration"]

    try:
        led.fadeRGB(group, color_name, float(duration))
        return Response(status=200)
    except Exception as e:
        logger.error(e)
        return Response(status=500)

@socketio.on("/robot/led/reset")
@app.route("/robot/led/reset", methods=["POST"])
@log("/robot/led/reset")
def reset_led():
    led_start("AllLeds")
    led_fade(["AllLeds", "white", 0])
