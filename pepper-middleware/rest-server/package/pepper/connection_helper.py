import qi
import logging
import os
from enum import Enum
import package.config as config
import time
from functools import lru_cache

from ..dummy import Dummy
from ..utilities import get_ip, is_host_reachable

CONNECTION_RETRIES = 6
RETRYING_MSG = "Couldn't gather all pepper services, retrying..."
REAL_ROBOT_SERVICE_COUNT = 104
RETRY_PAUSE_SECONDS = 6

class ConnectionType(Enum):
    REAL_ROBOT = 1,
    VIRTUAL_ROBOT = 2,
    DISCONNECTED = 3

logger = logging.getLogger(__name__)

if not config.IP:
    config.IP = os.environ["ROBOT_IP"]

if not config.FLASK_IP:
    config.FLASK_IP = get_ip()

if not config.FLASK_PORT:
    config.FLASK_PORT = int(os.environ["FLASK_PORT"])

if not config.MQTT_IP:
    config.MQTT_IP = get_ip()

if not config.MQTT_PORT:
    config.MQTT_PORT = int(os.environ["MQTT_PORT"])

logger.info("Using {} as Flask server IP.".format(config.FLASK_IP))

def get_service_list(session):
    list = []
    for service in session.services():
        list.append(service["name"])
    
    return list

def get_service(session, service):
    if not session or not session.isConnected():
        return Dummy(service)

    if service in get_service_list(session):
        return session.service(service)

    return Dummy(service)

def connect():
    logger.debug("Trying to connect to the robot with IP {} and port {}.".format(config.IP, config.PORT))
    
    if not is_host_reachable(config.IP, config.PORT):
        logger.info("The robot at {}:{} is not reachable.".format(config.IP, config.PORT))
        return None, ConnectionType.DISCONNECTED
    else:
        logger.debug("The robot at {}:{} is reachable.".format(config.IP, config.PORT))
    
    try:
        pepper = qi.Application(url="tcp://{}:{}".format(config.IP, config.PORT))
        pepper.start()
        session = pepper.session

        service_list, connection_type = get_service_list_retry(session)
        if connection_type == ConnectionType.REAL_ROBOT:
            session.listen("tcp://0.0.0.0:0") # actively listen for events from the robot, otherwise events won't reach our flask application

        logger.debug("Connected to robot with ip {} and port {}.".format(config.IP, config.PORT))
        return session, connection_type
    except RuntimeError as e:
        logger.debug("Can't connect to robot with ip {} and port {}.".format(config.IP, config.PORT))    
        return None, ConnectionType.DISCONNECTED
    
def get_service_list_retry(session):
    service_list = []
    connection_type = ConnectionType.VIRTUAL_ROBOT
    for i in range(0, CONNECTION_RETRIES):
        service_list = get_service_list(session)
        if len(service_list) >= REAL_ROBOT_SERVICE_COUNT:
            connection_type = ConnectionType.REAL_ROBOT
            break
        logger.info(RETRYING_MSG)
        print(RETRYING_MSG)
        time.sleep(RETRY_PAUSE_SECONDS)
    return service_list, connection_type