import logging
import numpy as np
import matplotlib.image

from flask import request, Response

from ...server import app, socketio
from ...pepper.connection import navigation
from ...decorator import log
from ...mqtt import socketio_wrapper

logger = logging.getLogger(__name__)

@socketio.on("/robot/navigation/to")
@app.route("/robot/navigation/to", methods=["POST"])
@log("/robot/navigation/to")
def navigate_to(data = None):
    if data:
        x, y = data

        x = float(x)
        y = float(y)
    else:
        x = request.get_json(force=True, silent=True)["x"]
        y = request.get_json(force=True, silent=True)["y"]
    
    try:
        future = navigation.navigateTo(x, y, _async=True)
        future.addCallback(navigation_finished)

        return Response(status=200)
    except Exception as e:
        logger.error(e)
        return Response(str(e), status=400)

def navigation_finished(future):
    success = future.value()

    if success:
        logger.debug("Navigation finished")
    else:
        logger.info("Navigation failed")
    
    socketio_wrapper("/event/navigation/finished", success)
    navigation.stopLocalization()

@socketio.on("/robot/navigation/explore")
@app.route("/robot/navigation/explore", methods=["POST"])
@log("/robot/navigation/explore")
def explore(radius=None):
    if not radius:
        radius = request.get_json(force=True, silent=True)["radius"]

    radius = float(radius)

    logger.info("Starting exploration with radius {}.".format(radius))
    exploration_future = navigation.explore(radius, _async=True)
    exploration_future.addCallback(exploration_finished)

    return Response(status=200)

@socketio.on("/robot/navigation/target")
@app.route("/robot/navigation/target", methods=["POST"])
@log("/robot/navigation/target")
def navigate_to_target(data = None):
    if data:
            x, y, theta = data
    else:
        x = request.get_json(force=True, silent=True)["x"]
        y = request.get_json(force=True, silent=True)["y"]
        theta = request.get_json(force=True, silent=True)["theta"]
    
    target = [x, y, theta]
    logger.info("Starting navigation to target {}.".format(target))

    navigation.startLocalization()
    navigaton_future = navigation.navigateToInMap(target, _async=True)
    navigaton_future.addCallback(navigation_finished)

    return Response(status=200)

def exploration_finished(exploration_future):
    logger.info("Finished exploration")

    map = navigation.getMetricalMap()
    data = map[4] #gets the data of the map 
    size = map[1] #size of the map
    size2 = map[2] #size of the map
    img = np.array(data).reshape(size, size2)
    img = (100 - img) * 2.5   #shapes the image to fit the map
    img = np.array(img, np.uint8)
    matplotlib.image.imsave("map.png", img)

    navigate_to_target((0, 0, 0))

@socketio.on("/robot/navigation/get")
@app.route("/robot/navigation/get", methods=["GET"])
@log("/robot/navigation/get")
def get_current_position():
    navigation.startLocalization()
    logger.info("The current position is {}.".format(navigation.getRobotPositionInMap()))
    navigation.stopLocalization()

    return Response(status=200)
