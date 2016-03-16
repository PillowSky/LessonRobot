# LessonRobot with Debian:jessie

FROM        debian:jessie
MAINTAINER  PillowSky <pillowsky@qq.com>

RUN apt-get update \
&&  apt-get install -y python python-tornado python-pyquery \
&&  apt-get clean \
&&  rm -rf /var/lib/apt/lists/* \
&&  mkdir /app

ADD . /app
WORKDIR /app

EXPOSE 8000
USER daemon
CMD ["python", "index.py"]
