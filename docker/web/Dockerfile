FROM python:3.9.6-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    LANG=C.UTF-8 \
    APP_HOME=/usr/src/app/ \
    CRYPTOGRAPHY_DONT_BUILD_RUST=1

WORKDIR $APP_HOME

RUN apk update && \
    apk add --no-cache curl postgresql-dev bash gcc python3-dev musl-dev openssl libffi-dev openssl-dev build-base \
     libressl-dev py-pip libffi-dev && \
    pip install --upgrade pip

COPY ./requirements.txt ./requirements.txt
RUN pip install -r ./requirements.txt

COPY . $APP_HOME
COPY ./docker/web/entrypoint.sh /

USER $USER
