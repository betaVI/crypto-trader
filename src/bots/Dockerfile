FROM python:3.9-buster

WORKDIR /usr/share/trader
COPY . /usr/share/trader/

RUN python3 -m pip install --upgrade pip && \
    pip3 install -r requirements.txt
ENV PYTHONPATH="/usr/share/trader"

ENV PYTHONUNBUFFERED 1
CMD [ "python3", "src/bots/databot.py" ]