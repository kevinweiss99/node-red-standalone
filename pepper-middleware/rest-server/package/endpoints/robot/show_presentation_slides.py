import logging
import urllib.parse

from flask import request, Response
from flask_socketio import emit

from ...server import app, socketio
from ...pepper.connection import tablet
from ...config import FLASK_IP, FLASK_PORT
from ...decorator import log

logger = logging.getLogger(__name__)

@socketio.on("/robot/presentation/show_slide")
@app.route("/robot/presentation/show_slide")
@log("/robot/presentation/slide")
def post_slide_browser(url=None):
    if not url:
        url = request.get_json(force=True, silent=True)["url"]
    if not tablet.showImage(url, _async=True):
        logger.warning("Website {} is not reachable.".format(url))
    
    return Response(status=200)

@socketio.on("/robot/tablet/image")
@app.route("/robot/tablet/image", methods=["POST"])
@log("/robot/tablet/image")
def show_image(url=None):
    if not url:
        url = request.get_json(force=True, silent=True)["url"]

    if not tablet.showImage(url, _async=True):
        logger.warning("Website {} is not reachable.".format(url))

        with app.test_request_context():
            emit("/robot/tablet/image/error", url, broadcast=True, namespace="/")
        return Response(status=400)

    return Response(status=200)

@socketio.on("/robot/tablet/clear")
@app.route("/robot/tablet/clear", methods=["POST"])
@log("/robot/tablet/clear")
def clear_tablet():
    show_default_image()

    return Response(status=200)
