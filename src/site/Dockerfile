FROM python:3.8-buster

WORKDIR /usr/share/trader
COPY . /usr/share/trader/

RUN python3 -m pip install --upgrade pip && \
    pip3 install -r requirements.txt
ENV PYTHONPATH="/usr/share/trader"

EXPOSE 18256
CMD ["gunicorn","--bind","0.0.0.0:18256","src.site.application:create_app()"]