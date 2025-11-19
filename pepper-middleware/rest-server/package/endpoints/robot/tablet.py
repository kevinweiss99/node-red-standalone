import logging
import urllib.parse

from flask import request, Response
from flask_socketio import emit

from ...server import app, socketio
from ...pepper.connection import tablet
from ...config import FLASK_IP, FLASK_PORT
from ...decorator import log

logger = logging.getLogger(__name__)

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

@socketio.on("/robot/tablet/text")
@app.route("/robot/tablet/text", methods=["POST"])
@log("/robot/tablet/text")
def show_text(text = None):
    if request and request.get_json(force=True, silent=True):
        text = request.get_json(force=True, silent=True).get("text", "")
    elif text is None:
        text = ""

    text = urllib.parse.quote(str(text))
    
    url = "http://{}:{}/tablet?text={}".format(FLASK_IP, FLASK_PORT, text)
    result = tablet.loadUrl(url, _async=True)

    if not result:
        logger.warning("Website {} is not reachable.".format(url))
        return Response(status=500)

    tablet.showWebview()

    return Response(status=200)

def show_default_image():
    show_image("http://{}:{}/static/img/default.png".format(FLASK_IP, FLASK_PORT))

show_default_image()
