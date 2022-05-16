#!/bin/sh

alembic upgrade head
gunicorn app.main:setup_app --workers 4 --worker-class aiohttp.GunicornUVLoopWebWorker --bind 0.0.0.0:8000
