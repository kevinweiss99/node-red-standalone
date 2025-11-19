import qi
import logging
import sys
import asyncio
from concurrent.futures import ThreadPoolExecutor
from flask_socketio import emit
import time
import urllib


from ..server import app
from .connection_helper import get_service, connect, ConnectionType
from ..mqtt import socketio_wrapper
from ..utilities import get_ip, is_host_reachable, shutdown
import package.config as config

logger = logging.getLogger(__name__)
session, connection_type = connect()
logger.info("Connection type: " + str(connection_type))
print("Connection type:", str(connection_type))

with app.test_request_context():
    emit("/update/connection_type", connection_type, broadcast=True, namespace="/")


animation = get_service(session, "ALAnimationPlayer")
awareness = get_service(session, "ALBasicAwareness")
audio = get_service(session, "ALAudioDevice")
behavior = get_service(session, "ALBehaviorManager")
barcode = get_service(session, "ALBarcodeReader")
battery = get_service(session, "ALBattery")
compass = get_service(session, "ALVisualCompass")
connection_manager = get_service(session, "ALConnectionManager")
face_detection = get_service(session, "ALFaceDetection")
led = get_service(session, "ALLeds")
life = get_service(session, "ALAutonomousLife")
memory = get_service(session, "ALMemory")
motion = get_service(session, "ALMotion")
navigation = get_service(session, "ALNavigation")
photo = get_service(session, "ALPhotoCapture")
posture = get_service(session, "ALRobotPosture")
speaking_movement = get_service(session, "ALSpeakingMovement")
speech_recognition = get_service(session, "ALSpeechRecognition")
system = get_service(session, "ALSystem")
tablet = get_service(session, "ALTabletService")
temperature = get_service(session, "ALBodyTemperature")
touch = get_service(session, "ALTouch")
tts = get_service(session, "ALTextToSpeech")
tts_animated = get_service(session, "ALAnimatedSpeech")
video = get_service(session, "ALVideoDevice")

ERROR_NO_CONNECTION = "No connection to robot could be established"

if connection_type == ConnectionType.DISCONNECTED:
    print(ERROR_NO_CONNECTION)
    logger.error(ERROR_NO_CONNECTION)
    shutdown()




