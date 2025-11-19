import logging

from threading import Event, Thread
from time import sleep, time
from flask import Flask, Response
from ..server import app
logger = logging.getLogger(__name__)

@app.route("/stream/<int:frequency>")
def stream(frequency: int):
    return Response(generate_stream(frequency),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


def generate_stream(frequency: int):
    imageLoader = ImageLoader(frequency)

    while True:
        image = imageLoader.image
        if image is not None:
            yield b"--frame\nContent-Type: image/jpeg\n\n" + image

        sleep(1/60)

class ImageLoader:
    def __init__(self, frequency):
        self.frequency = frequency

        self.stop = Event()
        self.image = None

        self.thread = Thread(target=self.worker)
        self.thread.start()

    def worker(self):
        try:
            i = 0
            while not self.stop.is_set():
                # Get current image in separate thread
                i = i % 2
                i += 1
                with open("./package/static/img/{}.png".format(i), "rb") as f:
                    self.image = f.read()

                sleep(1 / self.frequency)
        except Exception as e:
            logger.debug(e)