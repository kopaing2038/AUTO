FROM python:3.9-slim-buster
WORKDIR /app

RUN apt update -y
RUN apt install gcc -y
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD python3 -m bot