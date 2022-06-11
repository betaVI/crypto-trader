FROM python:3.8-buster

RUN python3 --version
RUN python3 -m pip install --upgrade pip

WORKDIR /usr/share/trader
COPY ./src /usr/share/trader
RUN pip3 install -r requirements.txt
# WORKDIR /usr/share/trader

# ENV PYTHONPATH="/usr/share/trader"
CMD [ "python3", "-u", "src/bots/databot.py" ]