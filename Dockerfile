FROM python:3.9

WORKDIR /code

COPY ./requirements.txt ./requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app ./app
COPY ./start.sh ./start.sh

ENV PYTHONPATH "/code/app"

CMD ["./start.sh"]
