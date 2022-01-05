FROM python:3.8-buster

RUN python3 --version
RUN python3 -m pip install --upgrade pip

# RUN mkdir --parents /usr/share/trader
WORKDIR /usr/share/trader
COPY ./src /usr/share/trader
RUN pip3 install -r requirements.txt
WORKDIR /usr/share/trader/bots

ENV PYTHONPATH="/usr/share/trader"
CMD [ "python3", "-u", "databot.py" ]