FROM ubuntu:22.04

WORKDIR /home/

COPY qi-3.1.1-cp310-cp310-linux_x86_64.whl .

RUN apt-get update
RUN apt-get install curl -y
RUN apt-get install python3-pip -y
RUN apt-get install libicu-dev -y

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install qi-3.1.1-cp310-cp310-linux_x86_64.whl --force-reinstall

EXPOSE 5000

CMD /home/run.sh
