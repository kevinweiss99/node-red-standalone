import logging
import traceback
import sys
from package.logger import *


logger = logging.getLogger(__name__)

# print("""
# ██████╗ ██████╗  ██████╗      ██╗███████╗ ██████╗████████╗    ██╗    ██╗██████╗  █████╗ ██████╗ ███████╗
# ██╔══██╗██╔══██╗██╔═══██╗     ██║██╔════╝██╔════╝╚══██╔══╝    ██║    ██║██╔══██╗██╔══██╗██╔══██╗██╔════╝
# ██████╔╝██████╔╝██║   ██║     ██║█████╗  ██║        ██║       ██║ █╗ ██║██████╔╝███████║██████╔╝███████╗
# ██╔═══╝ ██╔══██╗██║   ██║██   ██║██╔══╝  ██║        ██║       ██║███╗██║██╔══██╗██╔══██║██╔═══╝ ╚════██║
# ██║     ██║  ██║╚██████╔╝╚█████╔╝███████╗╚██████╗   ██║       ╚███╔███╔╝██║  ██║██║  ██║██║     ███████║
# ╚═╝     ╚═╝  ╚═╝ ╚═════╝  ╚════╝ ╚══════╝ ╚═════╝   ╚═╝        ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚══════╝                            

#                                       by Kai Ruske and Michel Weike
# """)

try:
    from package.pepper.connection_helper import *
    from package.server import *
    from package.socket import *
    from package.mqtt import *
    from package.pepper.connection import *
    from package.pepper.event_helper import *
    from package.endpoints.debug import *
    from package.endpoints.page_generator import *
    from package.endpoints.log import *
    from package.endpoints.stream import *
    from package.endpoints.esp.esp import *
    from package.endpoints.esp.thermal_camera import *
    from package.endpoints.session import *

    from package.endpoints.robot.animation import *
    from package.endpoints.robot.audio import *
    from package.endpoints.robot.awareness import *
    from package.endpoints.robot.behavior import *
    from package.endpoints.robot.battery import *
    from package.endpoints.robot.face_detection import *
    from package.endpoints.robot.led import *
    from package.endpoints.robot.life import *
    from package.endpoints.robot.motion import *
    from package.endpoints.robot.navigation import *
    from package.endpoints.robot.qr import *
    from package.endpoints.robot.system import *
    from package.endpoints.robot.speech_recognition import *
    from package.endpoints.robot.tablet import *
    from package.endpoints.robot.temperature import *
    from package.endpoints.robot.touch import *
    from package.endpoints.robot.tts import *
except Exception as e:
    logger.critical(traceback.format_exc())
    logger.critical("Exiting application due to unhandled exception")
    sys.exit(4)
