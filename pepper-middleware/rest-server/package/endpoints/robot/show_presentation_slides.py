import logging
import urllib.parse

from flask import request, Response
from flask_socketio import emit

from ...server import app, socketio
from ...pepper.connection import tablet
from ...config import FLASK_IP, FLASK_PORT
from ...decorator import log

logger = logging.getLogger(__name__)

from flask import request, Response
from flask_socketio import SocketIO, emit

socketio = SocketIO()
last_slide_url = None

@socketio.on("/robot/presentation/show_slide")
@app.route("/robot/presentation/show_slide", methods=["POST"])
@log("/robot/presentation/slide")
def post_slide_browser(url=None):
    global last_slide_url

    if not url:
        data = request.get_json(force=True, silent=True)
        url = data.get("url")

    last_slide_url = url  # store it

    # Show the image on the tablet
    if not tablet.showImage(url, _async=True):
        logger.warning(f"Website {url} is not reachable.")

    # Emit so all listeners get the update
    socketio.emit("/robot/presentation/current_slide", {"url": url})

    return Response(status=200)

@socketio.on("/robot/presentation/current_slide")
@app.route("/robot/tablet/current_slide")
@log("/robot/tablet/current_slide")
def show_image():
    global last_slide_url

    if not last_slide_url:
        return Response("No slide set", status=404)
    img_response = requests.get(last_slide_url, stream=True)

    if img_response.status_code != 200:
        return Response("Unable to load slide image", status=404)

    # Gib Bilddaten direkt zurück
    return Response(
        img_response.content,
        mimetype=img_response.headers.get('Content-Type', 'image/jpeg')
    )


