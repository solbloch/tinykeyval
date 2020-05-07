FROM ubuntu:18.04

RUN apt-get update

RUN apt-get -y install python3 python3-pip libev-dev libleveldb-dev

COPY ./server.py server.py

RUN pip3 install --upgrade plyvel bottle requests bjoern
