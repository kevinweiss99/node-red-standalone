// using https://github.com/plapointe6/EspMQTTClient

#include "Config.h"
#include "Constants.h"
#include "EspMQTTClient.h"
#include <Adafruit_MLX90640.h>
#include <ArduinoJson.h>
#include <FastLED.h>

#define NEOPIXEL_PIN 0
#define NUM_LEDS 1
#define MLX90640_DEBUG

unsigned int FRAMESIZE = 768;
unsigned int FRAMETIME = 500;

Adafruit_MLX90640 mlx;
float frame[768];
bool isCameraRunning = false;
bool sendImages = false;
unsigned long lastImageTime = 0;

CRGB leds[NUM_LEDS];

void log(int level, String message);

EspMQTTClient client(
  WIFI_SSID,
  WIFI_PASSWORD,
  MQTT_BROKER);

void setup()
{
  Serial.begin(115200);
  Serial.println("setup");

  Wire.setClock(400000); // required to set the sample rate to 4HZ

  // LED
  pinMode(NEOPIXEL_I2C_POWER, OUTPUT);
  digitalWrite(NEOPIXEL_I2C_POWER, HIGH);
  FastLED.addLeds<NEOPIXEL, NEOPIXEL_PIN>(leds, NUM_LEDS);
  FastLED.setBrightness(5);

  // MQTT/OTA
  client.setMaxPacketSize(16384); // 16 kB
  client.enableOTA(OTA_PASSWORD);
  client.enableLastWillMessage("esp/connected", "False", true);
}

void onConnectionEstablished()
{
  Serial.println("connection established");
  client.subscribe("esp/startCamera", [](const String & payload)
  {
    Serial.println(payload);
    Serial.println("Starting camera");
    sendImages = payload == "True";
    startCamera();
  });

  client.subscribe("esp/stopCamera", [](const String & payload)
  {
    stopCamera();
  });

  client.publish("esp/connected", "True", true);

  if (mlx.begin(MLX90640_I2CADDR_DEFAULT, &Wire))
  {

    Serial.println("Setting resolution and refreshrate");
    mlx.setResolution(MLX90640_ADC_19BIT);
    mlx.setRefreshRate(MLX90640_2_HZ);
  } else {
    log(ERROR, "MLX90640 not found."); // error
  }
}

void loop()
{
  client.loop();

  cameraLoop();
}

void cameraLoop() {
  if (isCameraRunning &&
      millis() - lastImageTime > FRAMETIME) {
    lastImageTime = millis();

    if (!client.isConnected()) {
      Serial.println("ESP is not connected (WIFI/MQTT)");
      leds[0] = CRGB::Blue;
      FastLED.show();
      return;
    }

    Serial.println("getting Frame");
    if (mlx.getFrame(frame) != 0) {
      Serial.println("Failed");
    }

    sendData();
    leds[0] = CRGB::Black;
    FastLED.show();
  }
}

void startCamera() {
  Serial.println("Camera started");
  isCameraRunning = true;
  log(INFO, "Starting camera with framerate");
}

void stopCamera() {
  Serial.println("Camera stopped");
  isCameraRunning = false;
  log(INFO, "Stopped camera");
}

void sendData() {
  leds[0] = CRGB::Green;
  FastLED.show();

  if (sendImages) {
    uint8_t buf[sizeof(frame)];
    for (int i = 0; i < sizeof(frame) / 4; i++)
    {
      byte *bits;
      bits = (byte *)&frame[i];

      for (int j = 0; j < 4; j++)
      {
        buf[i * 4 + j] = bits[j];
      }
    }

    client.publish("esp/thermal/data", buf, static_cast<int>(sizeof(buf)), false);
  } else {
    float minMaxArr[2];
    getMinMax(minMaxArr);
    
    DynamicJsonDocument json(1024);
    json["min"] = minMaxArr[0];
    json["max"] = minMaxArr[1];

    String output;
    serializeJson(json, output);

    client.publish("esp/thermal/data", output);
  }
}

void getMinMax(float* resultPtr) {
  float maxV = frame[0];
  float minV = frame[0];
  for (int i = 0; i < FRAMESIZE; i++) {
    if (frame[i] > maxV) {
      maxV = frame[i];
    }

    if (frame[i] < minV) {
      minV = frame[i];
    }
  }
  resultPtr[0] = minV;
  resultPtr[1] = maxV;
}

void log(int level, String message)
{
  if (!client.isConnected())
  {
    return;
  }

  DynamicJsonDocument json(1024);
  json["level"] = level;
  json["serviceName"] = DEVICE_NAME;
  json["message"] = message;

  String output;
  serializeJson(json, output);

  client.publish("log", output);
}
