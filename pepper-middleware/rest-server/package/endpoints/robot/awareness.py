from flask import request, Response

from ...config import DEFAULT_BASIC_AWARENESS_TRACKING
from ...pepper.connection import awareness
from ...server import app, socketio
from ...decorator import log
from .motion import set_head_pitch, set_head_yaw

@socketio.on("/robot/awareness")
@app.route("/robot/awareness", methods=["POST"])
@log("/robot/awareness")
def set_awareness(enabled = None):
    if not enabled:
        enabled = request.get_json(force=True, silent=True)["enabled"]

    _set_awareness(enabled)

    return Response(status=200)

@log("/robot/_set_awareness")
def _set_awareness(enabled, yaw=0, pitch=-5):
    if enabled is True:
        awareness.resumeAwareness()
    else:
        awareness.pauseAwareness()
        # reset head to neutral position
        set_head_yaw(yaw)
        set_head_pitch(pitch)

awareness.setTrackingMode(DEFAULT_BASIC_AWARENESS_TRACKING)
awareness.setEngagementMode("FullyEngaged")
