import logging
from data.dataaccess import DataAccess;
from forms.TraderForm import TraderForm
from flask import Blueprint, request, jsonify, render_template
from bots.cpapi import CbApi
from data.traderrepository import TraderRepository

trader_api = Blueprint('trader_api',__name__)
cbapi = CbApi()
db = DataAccess()
tradersrepo = TraderRepository(db)

@trader_api.route('/api/traders', methods=["GET"])
def getTraders():
    traders = tradersrepo.fetchProductTraders()
    return jsonify(success=True, data=traders)

@trader_api.route('/api/traders/<id>', methods=["GET"])
def getTrader(id='0'):
    if id == '0':
        return jsonify(success=False, message="Missing ID"), 400
    trader = tradersrepo.fetchTrader(id)
    return jsonify(success=True, data=trader), 200

@trader_api.route('/form/traders', methods=["GET"])
def loadTraderForm():
    id = '0'
    if 'id' in request.values:
        id = request.values['id']
    product = ''
    if 'product' in request.values:
        product = request.values['product']

    form = initializeTraderForm(id, product)
    return render_template('traderform.html', form=form)
    
@trader_api.route('/api/traders/<id>/<status>', methods=["GET"])
def updateTraderStatus(id, status):
    result = tradersrepo.updateTraderStatus(id, status)
    if result == None:
        return jsonify(success=True, message="Successfully updated status")
    else:
        return jsonify(success=False, message="Failed to update status: "+ result)

@trader_api.route('/api/traders', methods=["POST"])
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
    result = tradersrepo.alterTrader(id, form.product.data, form.loglevel.data, baseaccount, quoteaccount, form.buyupperthreshold.data, form.buylowerthreshold.data, form.sellupperthreshold.data, form.selllowerthreshold.data, form.maxpurchaseamount.data)
    action = 'update' if id != '0' else 'create'
    if result == None:
        return jsonify(success=True, message="Successfully {}d".format(action)), 201
    else:
        return jsonify(success=False, message="Failed to {}: {}".format(action, result)), 400

@trader_api.route('/api/traders/<id>', methods=['DELETE'])
def deleteTrader(id='0'):
    if id == '0':
        return jsonify(success=False, message="Missing ID"), 400
    tradersrepo.deleteTrader(id)
    return jsonify(success=True, message="Successfully deleted"), 200

def initializeTraderForm(id='0', product=''):
    accounts = cbapi.getAccounts()
    balance = next(iter([a['balance'] for a in accounts if a['currency'] == 'USD']))
    totalused = tradersrepo.getTotalAllowedForTraders()
    if id != '0':
        form = TraderForm(data=tradersrepo.fetchTrader(id))
    else:
        form = TraderForm(product=product, loglevel=10)
    form.availablefunds = round(float(balance)-totalused, 2)
    form.loglevel.choices = [(key,value) for key,value in logging._levelToName.items() if key > 0]
    return form