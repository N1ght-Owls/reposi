FROM tiangolo/meinheld-gunicorn:python3.7

VOLUME ["/app"]

COPY ./requirements.txt /opt/requirements.txt

RUN [ "pip", "install", "-r", "/opt/requirements.txt" ]