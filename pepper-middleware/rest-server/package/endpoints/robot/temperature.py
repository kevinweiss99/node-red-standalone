from flask import Response

from ...server import app
from ...pepper.connection import memory
from ...decorator import log

@app.route("/robot/temperature")
@log("/robot/temperature")
def get_temperature():
    return Response(str(_get_temperature()), status=200)

def _get_temperature():
    temperature = memory.getData("Device/SubDeviceList/KneePitch/Temperature/Sensor/Value")

    if not temperature:
        temperature = "-"

    return temperature