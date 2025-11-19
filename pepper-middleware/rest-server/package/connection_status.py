import logging

logger = logging.getLogger(__name__)

def handle_connection_status(connected, serviceName):
    status = "connected" if connected else "disconnected"
    if serviceName:
        logger.info("Service {} {}".format(serviceName, status))
    else:
        logger.warning("Unknown service {}".format(status))