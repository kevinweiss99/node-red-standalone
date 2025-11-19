#!/bin/sh

python $ESP_OTA_PATH/espota.py \
    --ip $ESP_IP \
    -a $ESP_OTA_PW \
    -f /home/pepper/out/pepper.ino.bin \
    -d \
    -r \
    -P 10000
