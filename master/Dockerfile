FROM ubuntu:16.04

RUN apt-get update

RUN apt-get -y install python3 python3-pip libev-dev

COPY ./server.py server.py

RUN pip3 install plyvel bottle requests bjoern
