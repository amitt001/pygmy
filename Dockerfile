FROM ubuntu:18.04

LABEL name='pygmy'
LABEL version='1.0.0'
LABEL description='Pygmy(pygy.co) URL shortener'
LABEL vendor="Amit Tripathi"

RUN apt update -y && apt install python3-pip -y

WORKDIR /pygmy
ADD . /pygmy
RUN pip3 install -r requirements.txt

EXPOSE 8000

CMD ["python3", "run.py"]
