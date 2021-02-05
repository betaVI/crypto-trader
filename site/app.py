import os, sys
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from dataaccess import DataAccess
from forms.TraderForm import TraderForm
from bots.cpapi import CbApi

app = Flask(__name__)
app.config['SECRET_KEY'] = str(os.urandom(32))

cbapi = CbApi()
db = DataAccess()

@app.route('/')
def index():
    traders = db.fetchTraders()
    accounts = [a for a in cbapi.getAccounts() if float(a['balance']) > 0]
    form = TraderForm()
    form.product.choices = loadProductsDropDown()
    form.status.choices = loadStatusDropDown()
    templatedata = { 'traders': traders, 'accounts': accounts } #, 'form': form }
    return render_template('index.html', **templatedata)

@app.route('/<productid>/price', methods=["GET"])
def getPrice(productid):
    price = cbapi.getMarketPrice(productid)
    return jsonify(price)

@app.route('/product/prices', methods=["POST"])
def getProductPrices():
    result = {}
    if 'products' in request.json:
        products = request.json['products']
        for p in products:
            if p =='USD-USD':
                price = 1
            else:
                price =  cbapi.getMarketPrice(p)
            result[p] = price
    return jsonify(result)

@app.route('/trader/view/<id>')
def viewTrader(id):
    trader = db.fetchTrader(id)
    product = cbapi.getProduct(trader['product'])
    templatedata = { 'trader': trader, 'product': product }
    return render_template("traderView.html", **templatedata)

@app.route('/trader/delete/', methods=["POST"])
def deleteTrader():
    if 'id' in request.json:
        db.deleteTrader(request.json['id'])
        return jsonify(status="success", result="Successfully deleted")
    else:
        return jsonify(status="danger", result="Missing id")

@app.route('/alter/trader', methods=['GET','POST'])
@app.route('/alter/trader/<id>', methods=['GET','POST'])
def alterTrader(id='0'):
    if id != '0':
        trader = db.fetchTrader(id)
        form = TraderForm(data=trader)
        form.title = 'Edit Trader'
    else:
        form = TraderForm()
    form.product.choices = loadProductsDropDown()
    form.status.choices = loadStatusDropDown()
    if request.method == "GET":
        return render_template('traderform.html', form=form)
    if form.validate_on_submit():
        product = cbapi.getProduct(form.product.data)
        print(product)
        accounts = cbapi.getAccounts()
        baseaccount = next(iter([a['id'] for a in accounts if a['currency'] == product['base_currency']]), None)
        print(baseaccount)
        quoteaccount = next(iter([a['id'] for a in accounts if a['currency'] == product['quote_currency']]), None)
        print(quoteaccount)
        result = db.alterTrader(id, form.product.data, baseaccount, quoteaccount, form.buyupperthreshold.data, form.buylowerthreshold.data, form.sellupperthreshold.data, form.selllowerthreshold.data, 0, form.status.data)
        action = 'create' if id == '0' else 'update'
        if result == None:
            return jsonify(status="success", result="Successfully " + action + "d")
        else:
            return jsonify(status="danger", result="Failed to " + action + ": " + result)
    else:
        return jsonify(status="danger", result=form.errors)

def loadProductsDropDown():
    products = cbapi.getProducts()
    sortedproducts = [p['id'] for p in products if p['id'].endswith('USD')]
    sortedproducts.sort()
    return [('','Select a Product')] + [(p,p) for p in sortedproducts]

def loadStatusDropDown():
    statuses = db.fetchStatuses()
    return [(s['id'],s['name']) for s in statuses]

if __name__ == '__main__':
    app.run(debug=True, port=18256, host='0.0.0.0')