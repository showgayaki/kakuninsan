FROM nginx:latest

RUN apt-get update -y && apt-get upgrade -y
RUN apt-get -y install locales && localedef -f UTF-8 -i ja_JP ja_JP.UTF-8
ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:ja
ENV LC_ALL ja_JP.UTF-8
ENV TERM xterm
ENV TZ JST-9

RUN apt-get install python3 python3-pip -y
RUN pip install pipenv
RUN mkdir /var/kakuninsan
COPY . /var/kakuninsan
WORKDIR /var/kakuninsan
RUN pipenv install --system --deploy

WORKDIR /var/kakuninsan/web/src
RUN apt-get install -y nodejs npm
RUN npm install n -g
RUN n stable
RUN apt-get purge -y nodejs npm
RUN exec /bin/bash -l
RUN npm install
