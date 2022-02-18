#!/bin/bash

gunicorn main:my_web_app --bind :8080 --reload --worker-class aiohttp.GunicornWebWorker
exec "$@"
