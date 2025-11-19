#!/bin/sh

# flask run --host=0.0.0.0 --port=5000
# gunicorn --config gunicorn_config.py app:app --worker-class eventlet
 gunicorn \
 --worker-class eventlet \
 -w 1 \
 --threads 100 \
 -b 0.0.0.0:${FLASK_PORT} \
 --reload app:app
# python3 -m app