FROM python:3.10.6

WORKDIR /birbia-station

ENV ENV_IS_DEV=False
ENV BOT_TOKEN="Production_token_here"
ENV BOT_DEV_TOKEN="Developer_token_here"
ENV PREFIX="birbia"
ENV DEV_PREFIX="birbia-beta"
ENV DISCONNECT_DELAY=600
ENV CMD_TIMEOUT=2
ENV MAX_CACHE_ENTRIES=20
ENV LANGUAGE=en
ENV LOG_LEVEL="INFO"
ENV AI_MODEL_AUTH_TOKEN="auth_tkn"

COPY . .

RUN apt-get install ca-certificates

RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y ffmpeg

CMD [ "python", "-u", "main.py" ]