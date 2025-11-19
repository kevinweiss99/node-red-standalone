from flask import Response

from ...server import app
from ...pepper.connection import battery
from ...decorator import log

@app.route("/robot/battery")
@log("/robot/battery")
def get_battery_percentage():
    return Response(str(_get_battery_percentage()), status=200)

def _get_battery_percentage():
    battery_percentage = battery.getBatteryCharge()
    
    if not battery_percentage:
        battery_percentage = "-"

    return battery_percentage