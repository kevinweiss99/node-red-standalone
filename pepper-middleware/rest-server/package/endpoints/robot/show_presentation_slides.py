import logging
import urllib.parse
import requests

from flask import request, Response
from flask_socketio import emit

from ...server import app, socketio
from ...pepper.connection import tablet
from ...config import FLASK_IP, FLASK_PORT
from ...decorator import log

logger = logging.getLogger(__name__)

from flask import request, Response
from flask_socketio import SocketIO, emit

@app.route("/robot/presentation/show_slide", methods=["POST"])
@log("/robot/presentation/show_slide")
def post_slide_browser(url=None):
    try:
        if not url:
            data = request.get_json(force=True, silent=True)
            url = data.get("url")

        if not tablet.showImage(url, _async=True):
            logger.warning(f"Website {url} is not reachable.")

        img_response = requests.get(url, stream=True)
        if not img_response:
            logger.warning(f"Failed to retrieve {url}..")
            return Response(status=400)

        socketio.emit("/robot/presentation/show_slide", {"url": url})
        return Response(img_response.content, mimetype=img_response.headers.get('Content-Type', 'image/jpeg'),status=200)
    except Exception as e:
        print(f"e: {e}")