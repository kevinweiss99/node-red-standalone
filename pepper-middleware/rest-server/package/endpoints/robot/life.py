from flask import request, Response

from ...server import app, socketio
from ...pepper.connection import life
from ...decorator import log

@socketio.on("/robot/life/awareness")
@app.route("/robot/life/awareness", methods=["POST"])
@log("/robot/life/awareness")
def set_basic_awareness_enabled(enabled = None):
    if not enabled:
        enabled = request.get_json(force=True, silent=True)["enabled"]

    life.setAutonomousAbilityEnabled("BasicAwareness", enabled)

    return Response(status=200)
