import os, sys
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flask import Flask, render_template, request, redirect, url_for
from dataaccess import DataAccess
from forms.TraderForm import TraderForm
from bots.cpapi import CbApi

app = Flask(__name__)
app.config['SECRET_KEY'] = str(os.urandom(32))

path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cbapi = CbApi()
db = DataAccess(path)

@app.route('/')
def index():
    traders = db.fetchTraders()
    templatedata = { 'title': 'Traders', 'traders': traders }
    return render_template('index.html', **templatedata)

@app.route('/trader/alter', methods=['get','post'])
@app.route('/trader/alter/<id>', methods=['get','post'])
def alterTrader(id=0):
    form = TraderForm()
    products = cbapi.getProducts()
    sortedproducts = [p['id'] for p in products if 'USD' in p['id']]
    sortedproducts.sort()
    form.product.choices = [('','Select a Product')] + [(p,p) for p in sortedproducts]
    if form.validate_on_submit():
        product = next(iter([p for p in products if p['id'] == form.product.data]), None)
        print(product)
        accounts = cbapi.getAccounts()
        baseaccount = next(iter([a for a in accounts if a['currency'] == product['base_currency']]), None)
        print(baseaccount)
        qouteaccount = next(iter([a for a in accounts if a['currency'] == product['quote_currency']]), None)
        print(qouteaccount)
        db.insertTrader(form.product.data, baseaccount, qouteaccount, form.buyupperthreshold.data, form.buylowerthreshold.data, form.sellupperthreshold.data, form.selllowerthreshold.data)
        return redirect(url_for('index'))
    templatedata = { 'title': 'Add Trader', 'form': form }
    return render_template('traderAlter.html', **templatedata)

if __name__ == '__main__':
    app.run(debug=True, port=18256, host='0.0.0.0')