# leave None to get the value from the environment variable ROBOT_IP
IP = None
PORT = "9559"

# leave None to automatically get the ip
FLASK_IP = None
FLASK_PORT = None

# leave None to automatically get the ip and port
MQTT_IP = None
MQTT_PORT = None

# camera settings
CAMERA_UPDATE_INTERVAL = 500

# leave None to automatically set the name
LOG_PATH = None

# eastereggs
EASTER_EGGS = False

# DEPRECATED events to trigger Socket.IO messages
# SUBSCRIBED_SERVICES = [
    # {"service_name": "ALMemory", "event": "BarcodeReader/BarcodeDetected"},
    # {"service_name": "ALMemory", "event": "BatteryChargeChanged"},
    # {"service_name": "ALMemory", "event": "FaceDetected"},
    # {"service_name": "ALMemory", "event": "TextDone"},
    # {"service_name": "ALMemory", "event": "TouchChanged"},
    # {"service_name": "ALMemory", "event": "WordRecognized"},
# ]

# prefix used to identify custom animations on pepper (those need to be created through choregraphe)
BEHAVIOR_PREFIX = "masterarbeit-pepper"

# basic awareness tracking: ["Head","BodyRotation","WholeBody","MoveContextually"] see http://doc.aldebaran.com/2-4/naoqi/interaction/autonomousabilities/albasicawareness.html#albasicawareness-tracking-modes
DEFAULT_BASIC_AWARENESS_TRACKING = "WholeBody"

