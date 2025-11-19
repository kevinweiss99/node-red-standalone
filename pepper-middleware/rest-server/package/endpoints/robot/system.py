from flask import Response

from ...pepper.connection import system
from ...server import app, socketio
from ...decorator import log
from ...dummy import Dummy

@app.route("/robot/system/version")
@log("/robot/system/version")
def get_version():
    version = system.systemVersion()

    return Response(version, status=200)

@app.route("/robot/system/name")
@log("/robot/system/name")
def get_name():
    return Response(_get_name(), status=200)

@socketio.on("/robot/system/shutdown")
@app.route("/robot/system/shutdown", methods=["POST"])
@log("/robot/system/shutdown")
def shutdown():
    system.shutdown(_async=True)

    return Response(status=200)

@socketio.on("/robot/system/reboot")
@app.route("/robot/system/reboot", methods=["POST"])
@log("/robot/system/reboot")
def reboot():
    system.reboot(_async=True)

    return Response(status=200)

def _get_name():
    name = system.robotName()

    if isinstance(name, Dummy):
        name = "-"
        
    return name