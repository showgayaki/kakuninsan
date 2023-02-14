FROM python:3.9-slim-bullseye AS build

WORKDIR /tmp
COPY requirements.txt /tmp

RUN apt-get update -y && apt-get upgrade -y \
&& rm -rf /var/lib/apt/lists/* && apt-get clean && apt-get autoclean && apt-get autoremove \
&& pip install --upgrade pip setuptools \
&& pip install -r requirements.txt


FROM gcr.io/distroless/python3-debian11

COPY --from=build /usr/local/lib/python3.9/site-packages /usr/lib/python3.9/dist-packages
COPY . /var/kakuninsan

ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:ja
ENV LC_ALL ja_JP.UTF-8
ENV TERM xterm
ENV TZ JST-9

# WORKDIR /var/kakuninsan/web/src
# RUN apt-get install -y nodejs npm
# RUN npm install n -g
# RUN n stable
# RUN apt-get purge -y nodejs npm
# RUN exec /bin/bash -l
# RUN npm install
