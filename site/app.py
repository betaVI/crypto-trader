import os, sys, time, decimal, flask.json
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from dataaccess import DataAccess
from forms.TraderForm import TraderForm
from bots.cpapi import CbApi

class JsonEncoder(flask.json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return str(obj)
        return super(JsonEncoder, self).default()

app = Flask(__name__)
app.json_encoder = JsonEncoder
app.config['SECRET_KEY'] = str(os.urandom(32))

import traderscontroller

cbapi = CbApi()
db = DataAccess()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/accounts', methods=["GET"])
def getAccounts():
    accounts=[]
    for account in cbapi.getAccounts():
        if float(account['balance'])>0:
            account['currencyvalue'] = 1 if account['currency']=='USD' else 0
            accounts.append(account)
    return jsonify(success=True, data=accounts), 200

@app.route('/api/products')
def getProducts():
    products = [p['id'] for p in cbapi.getProducts() if p['id'].endswith('USD')]
    return jsonify(success=True, data=products)

if __name__ == '__main__':
    app.run(debug=True, port=18256, host='0.0.0.0')