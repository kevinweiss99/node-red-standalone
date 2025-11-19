#!/bin/sh

# build rest-server container
docker build -t rest-server rest-server/

# build mosquitto container
docker build -t mosquitto mosquitto/

docker build -t mdns mdns/