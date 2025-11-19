FROM python:3.10-slim-bullseye

WORKDIR /home/pepper/

RUN apt-get update && apt-get install curl -y

RUN curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh

COPY arduino-cli.yaml .
RUN bin/arduino-cli core update-index
RUN bin/arduino-cli core install "esp32:esp32"
RUN pip install pyserial

RUN bin/arduino-cli lib install --git-url https://github.com/plapointe6/EspMQTTClient.git
RUN bin/arduino-cli lib install "Adafruit MLX90640"
RUN bin/arduino-cli lib install "PubSubClient"
RUN bin/arduino-cli lib install "FastLED"

COPY upload.sh .

COPY pepper/ .

RUN bin/arduino-cli compile --fqbn "esp32:esp32:adafruit_feather_esp32_v2"

EXPOSE 10000

CMD /home/pepper/upload.sh
