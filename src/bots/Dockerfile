FROM python:3-buster

RUN python3 --version
RUN python3 -m pip install --upgrade pip

RUN mkdir --parents /usr/share/trader
WORKDIR /app/share/trader
COPY ./src /app/share/trader
RUN pip3 install -r requirements.txt
WORKDIR /app/share/trader/bots

ENV PYTHONPATH="/app/share/trader"
CMD [ "python3", "-u", "databot.py" ]