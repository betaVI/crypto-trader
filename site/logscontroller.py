import os, time, datetime
from __main__ import app, db
from flask import Flask, request, jsonify, render_template
from data.logsrepository import LogsRepository

logsrepo = LogsRepository(db)

@app.route('/api/loggers', methods=["GET"])
def getLoggers():
    loggers = logsrepo.getLoggers()
    return jsonify(success=True, data=loggers)

@app.route('/api/logs/<pagesize>/<pageno>/<sort>/<sortdir>', methods=["POST"])
def getLogs(pagesize='10',pageno='1',sort='createdat',sortdir='desc'):
    filters = []
    if len(request.json) >0:
        for f in request.json['filters']:
            filters.append(translateFilter(f))
    logs, totalcount = logsrepo.fetchLogs(int(pageno), int(pagesize), sort, sortdir, filters)
    return jsonify(success=True, totalcount=totalcount, data=logs)

def translateFilter(filter):
    if filter['name']=='Logger':
        filter['name'] = 'loggername'
    if filter['name'] == 'Timestamp':
        filter['name'] = 'createdat'
        filter['value'] = getInterval(filter['value'])
        filter['operator'] = '>'

    return filter

def getInterval(interval):
    now = datetime.datetime.now()
    mapping = {
        "1m":  datetime.timedelta(minutes=-1),
        "15m":  datetime.timedelta(minutes=-15),
        "1h":  datetime.timedelta(hours=-1),
        "6h":  datetime.timedelta(hours=-6),
        "1d":  datetime.timedelta(days=1),
        "1w":  datetime.timedelta(weeks=1),
    }
    return now + mapping[interval]