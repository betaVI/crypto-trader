FROM python:3.8
RUN apt-get update
RUN apt-get install -y --no-install-recommends
RUN python3 -m pip install --upgrade pip

WORKDIR /app
COPY ./src /app
RUN pip3 install -r requirements.txt
WORKDIR /app/site

ENV PYTHONPATH="/app"

EXPOSE 18256

CMD ["gunicorn","--bind","0.0.0.0:18256","app:app"]