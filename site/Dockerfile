FROM python:3.8
RUN apt-get update
RUN apt-get install -y --no-install-recommends
RUN python3 -m pip install --upgrade pip

WORKDIR /app
COPY . /app
RUN pip3 install -r requirements.txt
WORKDIR /app/site

ENV PYTHONPATH="/app"
ENTRYPOINT [ "python3" ]
CMD [ "app.py" ]