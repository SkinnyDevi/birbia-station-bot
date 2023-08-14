FROM python:3.10.6

WORKDIR /birbia-station

ENV ENV_IS_DEV=False
ENV BOT_TOKEN="Production_token_here"
ENV BOT_DEV_TOKEN="Developer_token_here"
ENV DISCONNECT_DELAY=600
ENV CMD_TIMEOUT=2

COPY . .

RUN pip install poetry
RUN poetry install

RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y ffmpeg

CMD [ "poetry", "run", "bot" ]