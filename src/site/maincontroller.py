import os, traceback, logging
from dependency_injector.wiring import Provide, inject
from flask import Blueprint, request, jsonify, render_template
from src.data.dataaccess import DataAccess
from src.services.cpapi import CbApi
from src.container import Container

main_api = Blueprint('main_api',__name__)

@main_api.route('/')
@main_api.route('/diagnostics')
@main_api.route('/settings')
@inject
def index():
    return render_template('index.html')

@main_api.route('/api/accounts', methods=["GET"])
@inject
def getAccounts(cbapi: CbApi = Provide[Container.cbapi_client]):
    accounts=[]
    result = cbapi.getAccounts()
    for account in result:
        if float(account['balance'])>0:
            account['currencyvalue'] = 1 if account['currency']=='USD' else 0
            accounts.append(account)
    return jsonify(success=True, data=accounts), 200

@main_api.route('/api/products')
@inject
def getProducts(cbapi: CbApi = Provide[Container.cbapi_client]):
    products = [p['id'] for p in cbapi.getProducts() if p['id'].endswith('USD')]
    return jsonify(success=True, data=products)

@main_api.route('/api/settings', methods=["GET"])
@inject
def getSettings(db: DataAccess = Provide[Container.db]):
    try:
        loglevels = [(key,value) for key,value in logging._levelToName.items() if key > 0]
        settings = db.executeRead("SELECT interval, loglevel FROM settings")
        return jsonify(success=True, loglevels=loglevels, interval=int(settings[0]['interval']), loglevel=int(settings[0]['loglevel']))
    except Exception:
        return jsonify(success=False, message=traceback.format_exc())

@main_api.route('/api/settings', methods=["POST"])
@inject
def postSettings(db: DataAccess = Provide[Container.db]):
    try:
        if 'interval' not in request.json or 'loglevel' not in request.json:
            return jsonify(success=False, message='Missing parameters')
        interval = request.json['interval']
        loglevel = request.json['loglevel']
        db.execute('UPDATE settings SET interval=%s, loglevel=%s',(interval,loglevel))
        return jsonify(success=True, message='Successfully updated settings')
    except Exception:
        return jsonify(success=False, message=traceback.format_exc())

# @main_api.route('/api/system/')
# @inject
# def systemAction():
#     try:
#         if 'action' not in request.json:
#             return jsonify(success=False, message='Missing parameter')
#         action = request.json['action']
#         if action == 'reboot':
#             os.system('sudo reboot')
#             return jsonify(success=True, message='Successfully rebooted server')
#         elif action == 'shutdown':
#             os.system('sudo halt')
#             return jsonify(success=True, message='Successfully shutdown server')
#         else:
#             return jsonify(success=False, message='Unknown command "' + action +'" received')
#     except Exception:
#         return jsonify(success=False, message=traceback.format_exc())