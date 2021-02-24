import os, time
from __main__ import app, db
from flask import Flask, request, jsonify, render_template
from data.logsrepository import LogsRepository

logsrepo = LogsRepository(db)

@app.route('/api/logs/<pagesize>/<pageno>/<sort>/<sortdir>', methods=["GET"])
def getLogs(pagesize='10',pageno='1',sort='createdat',sortdir='desc'):
    logs, totalcount = logsrepo.fetchLogs(int(pageno), int(pagesize), sort, sortdir)
    return jsonify(success=True, totalcount=totalcount, data=logs)