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
    templatedata = { 'traders': traders, 'accounts': accounts }
    return render_template('index.html', **templatedata)

@app.route('/<productid>/price', methods=["GET"])
def getPrice(productid):
    price = cbapi.getMarketPrice(productid)
    return jsonify(price)

@app.route('/accounts/getbalances', methods=["POST"])
def getAccountBalances():
    result = {}
    if 'currencies' in request.json:
        currencies = request.json['currencies']
        for c in currencies:
            if c=='USD':
                price = 1
            else:
                price = cbapi.getMarketPrice(c+'-USD')
            result[c]=price
    return jsonify(result)

@app.route('/trader/view/<id>')
def viewTrader(id):
    trader = db.fetchTrader(id)
    product = cbapi.getProduct(trader['product'])
    templatedata = { 'trader': trader, 'product': product }
    return render_template("traderView.html", **templatedata)

@app.route('/trader/delete/<id>')
def deleteTrader(id):
    db.deleteTrader(id)
    flash("Successfully deleted", "success")
    return redirect(url_for('index'))

@app.route('/trader/alter', methods=['get','post'])
@app.route('/trader/alter/<id>', methods=['get','post'])
def alterTrader(id=0):
    title = 'Add Trader'
    id = int(id)
    if request.method == 'GET' and id != 0:
        title = 'Edit Trader'
        trader = db.fetchTrader(id)
        form = TraderForm(data=trader)#dict(zip(trader.keys(),trader)))
    else:
        form = TraderForm()
    statuses = db.fetchStatuses()
    form.status.choices = [(s['id'],s['name']) for s in statuses]
    products = cbapi.getProducts()
    sortedproducts = [p['id'] for p in products if p['id'].endswith('USD')]
    sortedproducts.sort()
    form.product.choices = [('','Select a Product')] + [(p,p) for p in sortedproducts]
    if form.validate_on_submit():
        product = next(iter([p for p in products if p['id'] == form.product.data]), None)
        print(product)
        accounts = cbapi.getAccounts()
        baseaccount = next(iter([a['id'] for a in accounts if a['currency'] == product['base_currency']]), None)
        print(baseaccount)
        quoteaccount = next(iter([a['id'] for a in accounts if a['currency'] == product['quote_currency']]), None)
        print(quoteaccount)
        result = db.alterTrader(id, form.product.data, baseaccount, quoteaccount, form.buyupperthreshold.data, form.buylowerthreshold.data, form.sellupperthreshold.data, form.selllowerthreshold.data, form.status.data)
        action = 'create' if id == 0 else 'update'
        if result == None:
            flash("Successfully " + action + "d", "success")
            return redirect(url_for('index'))
        flash("Failed to " + action + ": " + result, "danger")
    templatedata = { 'title': title, 'form': form }
    return render_template('traderAlter.html', **templatedata)

if __name__ == '__main__':
    app.run(debug=True, port=18256, host='0.0.0.0')