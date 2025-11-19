import os
import logging
import logging.handlers
import package.config as config

if not config.LOG_PATH:
    config.LOG_PATH = os.environ["ROBOT_NAME"].lower() + ".log"

logging.basicConfig(filename=config.LOG_PATH,
                    level=os.environ["LOG_LEVEL"],
                    format="%(asctime)s.%(msecs)03d %(levelname)s %(name)s.%(funcName)s: %(message)s",
                    datefmt="%d.%m.%Y %H:%M:%S")

logging.getLogger("socketio").setLevel(logging.ERROR)
logging.getLogger("engineio").setLevel(logging.ERROR)
logging.getLogger("werkzeug").setLevel(logging.ERROR)
