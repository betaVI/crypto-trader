FROM python:3.8
# RUN apt-get update
# RUN apt-get install -y --no-install-recommends
# RUN python3 -m pip install --upgrade pip

RUN mkdir --parents /app/share/trader
WORKDIR /app/share/trader
COPY ./src /app/share/trader
RUN pip3 install -r requirements.txt
WORKDIR /app/share/trader/site

ENV PYTHONPATH="/app/share/trader"

EXPOSE 18256

CMD ["gunicorn","--bind","0.0.0.0:18256","app:app"]