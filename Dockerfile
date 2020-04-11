#Work in Progress

FROM debian:buster

RUN [ "mkdir", "/app" ]
RUN [ "apt", "update" ]
RUN [ "apt", "upgrade", "-y" ]
RUN [ "apt", "install", "-y", "python3-pip", "sqlite3" ]

COPY app.py /app/

RUN [ "pip3", "install", "flask", "flask_dance", "flask_sqlalchemy" ]

EXPOSE 5000

CMD [ "python3", "/app/app.py" ]