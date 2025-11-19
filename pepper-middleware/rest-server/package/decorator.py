import logging

from flask import request, has_request_context
from functools import wraps
from paho.mqtt.client import Client

def log(path):
    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not has_request_context():
                if len(args) > 0 and isinstance(args[0], Client):
                    return handle_mqtt_log(func, args, kwargs)

                return handle_method_call(func, args, kwargs)

            return handle_socketio(path, func, args, kwargs)
        return wrapper
    return decorate

def handle_mqtt_log(func, args, kwargs):
    topic = args[2].topic

    try:
        payload = args[2].payload.decode()
    except UnicodeDecodeError:
        payload = args[2].payload

    logger = logging.getLogger("{}.{}".format(func.__module__, func.__name__))

    if len(payload) > 32:
        logger.debug("{} length: {} bytes".format(topic, len(payload)))
    else:
        logger.debug("{} {}".format(topic, payload))

    return func(*args, **kwargs)

def handle_method_call(func, args, kwargs):
    logger = logging.getLogger("{}.{}".format(func.__module__, func.__name__))

    logger.debug("{}.{}".format(args, kwargs))
    return func(*args, **kwargs)

def handle_socketio(path, func, args, kwargs):
    # Socket.IO context
    logger = logging.getLogger("{}.{}".format(func.__module__, func.__name__))
    if hasattr(request, "event"):
        parameter = args
        logger.debug("Socket.IO: {} {} {}".format(request.remote_addr, path, parameter))
    else:
        # HTTP context
        parameter = request.get_json(force=True, silent=True)
        logger.debug("HTTP: {} {} {}".format(request.remote_addr, path, parameter))

    return func(*args, **kwargs)
