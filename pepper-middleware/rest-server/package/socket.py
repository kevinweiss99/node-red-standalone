from flask import request

from .server import socketio
from .connection_status import handle_connection_status

@socketio.on("connect")
def on_connect():
    handle_connection_status(True, request.headers.get("serviceName"))

@socketio.on("disconnect")
def on_disconnect():
    handle_connection_status(False, request.headers.get("serviceName"))
