FROM python:3
USER root
RUN mkdir "app"

WORKDIR /usr/src/app

COPY requirements.txt requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
COPY . /usr/src/app
