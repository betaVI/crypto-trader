import os, time
from __main__ import app
from forms.TraderForm import TraderForm
from flask import Flask, request, jsonify, render_template
from bots.cpapi import CbApi
from dataaccess import DataAccess

cbapi = CbApi()
db = DataAccess()

@app.route('/api/traders', methods=["GET"])
def getTraders():
    traders = db.fetchTraders()
    return jsonify(success=True, data=traders), 200

@app.route('/api/traders/<id>', methods=["GET"])
def getTrader(id='0'):
    if id == '0':
        return jsonify(success=False, message="Missing ID"), 400
    trader = db.fetchTrader(id)
    return jsonify(success=True, data=trader), 200

@app.route('/form/traders', methods=["GET"])
@app.route('/form/traders/<id>', methods=["GET"])
def loadTraderForm(id='0'):
    form = initializeTraderForm(id)
    return render_template('traderform.html', form=form)

@app.route('/api/traders', methods=["POST"])
def createTrader():
    form = initializeTraderForm()
    if not form.validate_on_submit():
        return jsonify(success=False, errors = form.errors), 400
    id = form.traderid.data if form.traderid.data != '' else '0'
    product = cbapi.getProduct(form.product.data)
    print(product)
    accounts = cbapi.getAccounts()
    baseaccount = next(iter([a['id'] for a in accounts if a['currency'] == product['base_currency']]), None)
    print(baseaccount)
    quoteaccount = next(iter([a['id'] for a in accounts if a['currency'] == product['quote_currency']]), None)
    print(quoteaccount)
    result = db.alterTrader(id, form.product.data, baseaccount, quoteaccount, form.buyupperthreshold.data, form.buylowerthreshold.data, form.sellupperthreshold.data, form.selllowerthreshold.data, 0, form.status.data)
    action = 'update' if id != '0' else 'create'
    if result == None:
        return jsonify(success=True, message="Successfully {}d".format(action)), 201
    else:
        return jsonify(success=False, message="Failed to {}: {}".format(action, result)), 400

@app.route('/api/traders/<id>', methods=['DELETE'])
def deleteTrader(id='0'):
    if id == '0':
        return jsonify(success=False, message="Missing ID"), 400
    db.deleteTrader(id)
    return jsonify(success=True, message="Successfully deleted"), 200

def loadProductsDropDown(currentproduct):
    configproducts = [t['product'] for t in db.fetchConfiguredProducts() if t['product'] != currentproduct]
    products = cbapi.getProducts()
    sortedproducts = [p['id'] for p in products if p['id'].endswith('USD') and p['id'] not in configproducts]
    sortedproducts.sort()
    return [('','Select a Product')] + [(p,p) for p in sortedproducts]

def loadStatusDropDown():
    statuses = db.fetchStatuses()
    return [(s['id'],s['name']) for s in statuses]

def initializeTraderForm(id='0'):
    if id != '0':
        form = TraderForm(data=db.fetchTrader(id))
    else:
        form = TraderForm()
    form.product.choices = loadProductsDropDown(form.product.data)
    form.status.choices = loadStatusDropDown()
    return form