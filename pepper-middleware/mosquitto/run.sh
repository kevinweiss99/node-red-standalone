#!/bin/sh

rm /mosquitto/config/mosquitto.conf

echo "listener ${MQTT_PORT} 0.0.0.0" >> /mosquitto/config/mosquitto.conf
echo "allow_anonymous true" >> /mosquitto/config/mosquitto.conf
#echo "log_type all" >> /mosquitto/config/mosquitto.conf

# start mosquitto server
/usr/sbin/mosquitto -c /mosquitto/config/mosquitto.conf
