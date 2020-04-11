#Work in Progress

FROM debian:buster

RUN [ "mkdir", "/app" ]
RUN [ "apt", "update" ]
RUN [ "apt", "upgrade", "-y" ]
RUN [ "apt", "install", "-y", "python3-pip" ]

COPY app.py /app/

RUN [ "pip3", "install", "flask", "redis", "flask_dance" ]

CMD [ "python3", "/app/app.py" ]