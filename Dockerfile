# Dockerfile for LessonRobot

FROM debian:jessie
MAINTAINER PillowSky <pillowsky@qq.com>

# install runtime
RUN echo "deb http://mirrors.zju.edu.cn/debian/ jessie main" > /etc/apt/sources.list \
&&  apt-get update \
&&  apt-get install -y python python-tornado python-pyquery \
&&  apt-get clean \
&&  rm -rf /var/lib/apt/lists/* \
&&  mkdir /app

# install app
ADD . /app

EXPOSE 8000
WORKDIR /app
USER daemon
ENTRYPOINT ["python", "main.py"]