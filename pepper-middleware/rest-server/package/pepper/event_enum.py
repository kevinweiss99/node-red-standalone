from enum import Enum

class PepperEvents(str, Enum):
    """
    This enum contains some event names of the Pepper robot. This is not a exhaustive enum. 
    More events can be found in the documentation of the NAOqi framework (see http://doc.aldebaran.com/2-5/naoqi-eventindex.html).
    """
    FACE_DETECTED = "FaceDetected"
    QR_DETECTED = "BarcodeReader/BarcodeDetected"
    BATTERY_CHARGE_CHANGED = "BatteryChargeChanged"
    WORD_RECOGNIZED = "WordRecognized"
    TOUCH_CHANGED = "TouchChanged"