FROM ubuntu:16.04
MAINTAINER vslvcode

RUN apt-get update && \
apt-get install -y python3 python3-pip && \
pip3 install pytelegrambotapi && \
pip3 install currencyconverter && \
pip3 install requests[socks]

ADD app /root/app
ADD docker_id1.py /root/app

WORKDIR /root/app

ENTRYPOINT ["python3", "docker_PID1.py"]
