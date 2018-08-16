FROM ubuntu:16.04
MAINTAINER vslvcode

ADD requirements.txt /
ADD app /root/app
ADD docker_PID1.py /root/app

RUN apt-get update
RUN apt-get install -y python3 python3-pip
RUN pip3 install -r requirements.txt

WORKDIR /root/app
ENTRYPOINT ["python3", "docker_PID1.py"]
