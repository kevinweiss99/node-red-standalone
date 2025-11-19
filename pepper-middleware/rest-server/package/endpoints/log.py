import logging
import json

from flask import request, Response
from ast import literal_eval as make_tuple

from ..server import app, socketio, mqtt

@socketio.on("/log")
@app.route("/log", methods=["POST"])
def log_message(data = None):
    try:
        if data:
            level, message = data
            serviceName = request.headers.get("serviceName")
        else:
            level = request.get_json(force=True, silent=True)["level"]
            message = request.get_json(force=True, silent=True)["message"]
            serviceName = request.get_json(force=True, silent=True)["serviceName"]
        
        logger = logging.getLogger(serviceName)
        logger.log(level, "{} {}".format(request.remote_addr, message))

        return Response(status=200)
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(e)

        return Response(status=500)

@mqtt.on_topic("log")
def log_mqtt_message(client, userdata, message):
    try:
        payload = json.loads(message.payload.decode())
        level = int(payload["level"])
        message = payload["message"]
        serviceName = payload["serviceName"]

        logger = logging.getLogger(serviceName)
        logger.log(level, message)
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(e)
