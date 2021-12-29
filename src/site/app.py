import os, decimal, flask.json, traceback, logging
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from data.dataaccess import DataAccess
from forms.TraderForm import TraderForm
from bots.cpapi import CbApi
from traderscontroller import trader_api
from reportcontroller import reports_api
from orderscontroller import orders_api
from logscontroller import logs_api

load_dotenv()

class JsonEncoder(flask.json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return str(obj)
        return super(JsonEncoder, self).default()

app = Flask(__name__)
app.json_encoder = JsonEncoder
app.config['SECRET_KEY'] = str(os.urandom(32))

cbapi = CbApi()
db = DataAccess()

app.register_blueprint(trader_api)
app.register_blueprint(reports_api)
app.register_blueprint(orders_api)
app.register_blueprint(logs_api)

@app.route('/')
@app.route('/diagnostics')
@app.route('/settings')
def index():
    return render_template('index.html')

@app.route('/api/accounts', methods=["GET"])
def getAccounts():
    accounts=[]
    result = cbapi.getAccounts()
    for account in result:
        if float(account['balance'])>0:
            account['currencyvalue'] = 1 if account['currency']=='USD' else 0
            accounts.append(account)
    return jsonify(success=True, data=accounts), 200

@app.route('/api/products')
def getProducts():
    products = [p['id'] for p in cbapi.getProducts() if p['id'].endswith('USD')]
    return jsonify(success=True, data=products)

@app.route('/api/settings', methods=["GET"])
def getSettings():
    try:
        loglevels = [(key,value) for key,value in logging._levelToName.items() if key > 0]
        settings = db.executeRead("SELECT interval, loglevel FROM settings")
        return jsonify(success=True, loglevels=loglevels, interval=int(settings[0]['interval']), loglevel=int(settings[0]['loglevel']))
    except Exception:
        return jsonify(success=False, message=traceback.format_exc())

@app.route('/api/settings', methods=["POST"])
def postSettings():
    try:
        if 'interval' not in request.json or 'loglevel' not in request.json:
            return jsonify(success=False, message='Missing parameters')
        interval = request.json['interval']
        loglevel = request.json['loglevel']
        db.execute('UPDATE settings SET interval=%s, loglevel=%s',(interval,loglevel))
        return jsonify(success=True, message='Successfully updated settings')
    except Exception:
        return jsonify(success=False, message=traceback.format_exc())

@app.route('/api/system/')
def systemAction():
    try:
        if 'action' not in request.json:
            return jsonify(success=False, message='Missing parameter')
        action = request.json['action']
        if action == 'reboot':
            os.system('sudo reboot')
            return jsonify(success=True, message='Successfully rebooted server')
        elif action == 'shutdown':
            os.system('sudo halt')
            return jsonify(success=True, message='Successfully shutdown server')
        else:
            return jsonify(success=False, message='Unknown command "' + action +'" received')
    except Exception:
        return jsonify(success=False, message=traceback.format_exc())

if __name__ == '__main__':
    app.run(debug=True, port=18256, host='0.0.0.0')