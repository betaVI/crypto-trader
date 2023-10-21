import logging
from flask import Blueprint, request, jsonify, render_template
from dependency_injector.wiring import Provide, inject
from src.site.forms.TraderForm import TraderForm
from src.container import Container
from src.services.cpapi import CbApi
from src.data.traderrepository import TraderRepository

trader_api = Blueprint('trader_api',__name__)

@trader_api.route('/api/traders', methods=["GET"])
@inject
def getTraders(cbapi: CbApi = Provide[Container.cbapi_client], tradersrepo: TraderRepository = Provide[Container.traders_repo]):
    traders = tradersrepo.fetchProductTraders()
    accounts = [a['currency'] for a in cbapi.getAccounts()]
    allowedtraders = [t for t in traders if t["product"].split('-')[0] in accounts]
    return jsonify(success=True, data=allowedtraders)

@trader_api.route('/api/traders/<id>', methods=["GET"])
@inject
def getTrader(id='0', tradersrepo: TraderRepository = Provide[Container.traders_repo]):
    if id == '0':
        return jsonify(success=False, message="Missing ID"), 400
    trader = tradersrepo.fetchTrader(id)
    return jsonify(success=True, data=trader), 200

@trader_api.route('/form/traders', methods=["GET"])
@inject
def loadTraderForm(cbapi: CbApi = Provide[Container.cbapi_client], tradersrepo: TraderRepository = Provide[Container.traders_repo]):
    id = '0'
    if 'id' in request.values:
        id = request.values['id']
    product = ''
    if 'product' in request.values:
        product = request.values['product']

    form = initializeTraderForm(cbapi,tradersrepo, id, product)
    return render_template('traderform.html', form=form)

@trader_api.route('/api/traders/<id>/<status>', methods=["GET"])
@inject
def updateTraderStatus(id, status, tradersrepo: TraderRepository = Provide[Container.traders_repo]):
    result = tradersrepo.updateTraderStatus(id, status)
    if result == None:
        return jsonify(success=True, message="Successfully updated status")
    else:
        return jsonify(success=False, message="Failed to update status: "+ result)

@trader_api.route('/api/traders', methods=["POST"])
@inject
def createTrader(cbapi: CbApi = Provide[Container.cbapi_client], tradersrepo: TraderRepository = Provide[Container.traders_repo]):
    form = initializeTraderForm(cbapi, tradersrepo)
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
@inject
def deleteTrader(id='0', cbapi:CbApi = Provide[Container.cbapi_client], tradersrepo: TraderRepository = Provide[Container.traders_repo]):
    if id == '0':
        return jsonify(success=False, message="Missing ID"), 400
    tradersrepo.deleteTrader(id)
    return jsonify(success=True, message="Successfully deleted"), 200

def initializeTraderForm(cbapi: CbApi, tradersrepo: TraderRepository, id='0', product=''):
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