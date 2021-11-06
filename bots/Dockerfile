FROM python:3.8
RUN apt-get update
RUN apt-get upgrade -y --no-install-recommends
RUN python3 -m pip install --upgrade pip

WORKDIR /app
COPY . /app
RUN pip3 install -r requirements.txt
WORKDIR /app/bots

ENV PYTHONPATH="/app"
CMD [ "python3", "-u", "databot.py" ]