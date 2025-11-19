from ..pepper.connection import session
from ..server import app
from flask import jsonify, abort, after_this_request
import logging
import sys
import time
from ..config import IP
from ..utilities import is_host_reachable
from ..utilities import shutdown
from ..server import request_session

STATUS_MSG = "Lost session with pepper, shutting down..."
PEPPER_WEBSITE_PORT = 80

def is_pepper_reachable(): #Hacky mechanism to check if we the webserver is reachable. We check for a sure 404, since
                           #I don't know any /status endpoint in the pepper api
    try:
        response = request_session.get("http://" + IP + ":80/definetly-not-available", timeout=0.5)
        logging.warn(response)
        return response.status_code == 404
    except Exception as e:
        logging.error(e)
        return False

#Is meant to be called by docker healthcheck in an interval
@app.route("/pepper/session/shutdown-if-dead")
def shutdown_if_dead():
    if not session.isConnected() or not is_pepper_reachable():
        print(STATUS_MSG)
        logging.error(STATUS_MSG)
        shutdown()
    else:
        return jsonify({"status":"alive"}), 200
