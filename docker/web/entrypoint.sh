#!/bin/bash

echo "Waiting for postgres connection"

while ! nc -z db 5432; do
  sleep 0.1
done

echo "PostgreSQL started"


alembic upgrade head
gunicorn main:setup_app --bind :8000 --reload --worker-class aiohttp.GunicornUVLoopWebWorker
exec "$@"
