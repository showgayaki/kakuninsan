FROM python:3.8-slim-bullseye

RUN apt-get update -y && apt-get upgrade -y \
&& DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
&& apt-get -y install locales && localedef -f UTF-8 -i ja_JP ja_JP.UTF-8 \
&& pip install pipenv \
&& rm -rf /var/lib/apt/lists/* && apt-get clean && apt-get autoclean && apt-get autoremove

ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:ja
ENV LC_ALL ja_JP.UTF-8
ENV TERM xterm
ENV TZ JST-9

COPY . /var/kakuninsan
WORKDIR /var/kakuninsan
RUN pipenv install --system --deploy

# WORKDIR /var/kakuninsan/web/src
# RUN apt-get install -y nodejs npm
# RUN npm install n -g
# RUN n stable
# RUN apt-get purge -y nodejs npm
# RUN exec /bin/bash -l
# RUN npm install
