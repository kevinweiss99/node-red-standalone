import json
import struct
import numpy as np
import logging
logging.getLogger("matplotlib").setLevel(logging.WARNING) # i hate this
import matplotlib.pyplot as plt
import io

from flask_socketio import emit
from flask import Response, send_file, request

from ...decorator import log
from ...mqtt import mqtt
from ...server import app, socketio
from ..robot.awareness import _set_awareness

logger = logging.getLogger(__name__)
is_camera_running = False
send_images = False
buffer = io.BytesIO()
cb = None

@mqtt.on_topic("esp/thermal/data")
def image_received(client, userdata, message):
    try:
        payload = message.payload
        if send_images:
            buf = []
            for i in range(0, len(payload), 4):
                buf.append(*struct.unpack("<f", payload[i:i+4])) # little endian
            try:
                image = np.reshape(buf, (24, 32))
                min_temp = np.round(np.min(image), 1)
                max_temp = np.round(np.max(image), 1)

                trigger_temp_event(max_temp)
                update_camera_image(image, min_temp, max_temp)
                
            except Exception as e:
                logger.error(e)
        else:
            temps = json.loads(payload.decode("utf-8"))
            trigger_temp_event(round(temps["max"], 1))
    except Exception as e:
        logger.error(e)

@socketio.on("/camera/start")
@app.route("/camera/start", methods=["POST"])
@log("/camera/start")
def start_camera(send_imgs = None): # True = imgs will be transmitted | False = only min/max temps
    if send_imgs is None:
        send_imgs = request.get_json(force=True, silent=True)["send_imgs"]

    if send_imgs == "false": 
        send_imgs = False
    elif send_imgs == "true":
        send_imgs = True
    else:
        logger.warning("Invalid payload")
        return Response(status=403)

    global send_images
    send_images = send_imgs

    try:
        _set_awareness(False)
        mqtt.publish("esp/startCamera", payload=str(send_imgs))

        is_camera_running = True
        with app.test_request_context():
            emit("/update/camera_status", is_camera_running, broadcast=True, namespace="/")

        return Response(status=200)
    except Exception as e:
        logger.error(e)
        return Response(status=500)

@socketio.on("/camera/stop")
@app.route("/camera/stop", methods=["POST"])
@log("/camera/stop")
def stop_camera():
    try:
        _set_awareness(True)
        mqtt.publish("esp/stopCamera")

        is_camera_running = False
        with app.test_request_context():
            emit("/update/camera_status", is_camera_running, broadcast=True, namespace="/")

        return Response(status=200)
    except Exception as e:
        logger.error(e)
        return Response(status=500)

@app.route("/camera/frame")
@log("/camera/frame")
def get_last_image():
    return send_file("static/img/camera_frame.png")

@app.route("/camera/temp/set", methods=["POST"])
@log("/camera/temp/set")
def trigger_temp_event(max_temp=None):
    if max_temp is None:
        max_temp = request.get_json(force=True, silent=True)["max_temp"]

    with app.test_request_context():
        emit("/event/camera/temperature", max_temp, broadcast=True, namespace="/")
    
    return Response(status=200)

def get_color_map(cmap_name="gnuplot", max_norm=42, min_norm=10):
    cmap = plt.get_cmap(cmap_name)
    norm = plt.Normalize(min_norm, max_norm)
    return cmap(norm(36.))

def update_camera_image(image, min_temp, max_temp):
    plt.axis("off")
    plt.tight_layout() 

    plt.imshow(image, cmap="gnuplot", interpolation="bicubic")
    plt.title("Min Temp.: {}°C | Max Temp.: {}°C"
        .format(min_temp, max_temp),
        fontsize=17)

    cb = plt.colorbar()
    cb.ax.set_yticklabels(["{:.0f}°C".format(i) for i in cb.get_ticks()]) 
        
    #plt.savefig("./package/static/img/camera_frame.png")

    buffer.seek(0)
    plt.savefig(buffer, format="png", backend="WXAgg")
    buffer.seek(0)
    plt.clf()
    # plt.close()

    with app.test_request_context():
        emit("/update/camera", {"img_bytearray": buffer.read()}, broadcast=True, namespace="/")
    
def get_camera_status():
    global is_camera_running
    return is_camera_running
