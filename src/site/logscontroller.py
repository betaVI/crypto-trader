import datetime
from flask import Blueprint, request, jsonify
from dependency_injector.wiring import Provide, inject
from src.data.logsrepository import LogsRepository
from src.container import Container

logs_api = Blueprint('logs_api',__name__)

@logs_api.route('/api/loggers', methods=["GET"])
@inject
def getLoggers(logsrepo: LogsRepository = Provide[Container.logs_repo]):
    loggers = logsrepo.getLoggers()
    return jsonify(success=True, data=loggers)

@logs_api.route('/api/logs/<pagesize>/<pageno>/<sort>/<sortdir>', methods=["POST"])
@inject
def getLogs(pagesize='10',pageno='1',sort='createdat',sortdir='desc', logsrepo: LogsRepository = Provide[Container.logs_repo]):
    filters = []
    if 'filters' in request.json and len(request.json['filters']) >0:
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
        "1d":  datetime.timedelta(days=-1),
        "1w":  datetime.timedelta(weeks=-1),
    }
    return now + mapping[interval]