from configLoader import loadConfig
import time
import logging
from bots.libs.authenticated_client import AuthenticatedClient

class CbApi:
    def __init__(self):
        config = loadConfig('../coinbase.ini','credentials')
        self.client = AuthenticatedClient(config['key'], config['b64secret'], config['passphrase'], api_url=config['url'])
    
    def getProducts(self):
        products = self.client.get_products()
        #print(products)
        return products

    def getAccounts(self):
        accounts = self.client.get_accounts()
        # print(accounts)
        return accounts
        
    def getProduct(self, product_id):
        product = self.client.get_product(product_id)
        # print(product)
        # logging.info("[product] {}: {}".format(product_id, product['base_increment']))
        return product#['base_increment']
    
    def getAccountDetails(self, account_id):
        account = self.client.get_account(account_id)
        logging.info('[BALANCE] {}: {}'.format(account['currency'], account['balance']))
        return account

    def getMarketPrice(self, product_id):
        result = self.client.get_product_ticker(product_id)
        # logging.info('[PRICE] ' + product_id + ' ' + str(result['price']))
        return float(result['price'])

    def getRecentTrades(self, product_id, side, count):
        results = []
        trades = list(self.client.get_product_trades(product_id))
        for trade in trades:
            if trade['side'] == side:
                results.append(trade)
            if len(results) == count:
                break
        # logging.info("[TRADES] result: " + str(results))
        return [float(t['price']) for t in results]

    def placeMarketOrder(self, product_id, side, funds = None, size = None):
        result = self.client.place_market_order(product_id=product_id, side=side, size=size, funds=funds)
        logging.info('[API] Market Order Result: ' + str(result))
        orderid = result['id']
        fill = self._getOrderDetails(orderid)
        logging.info('[{}] {} BTC for ${} at {}/BTC'.format(side.upper(), fill['size'], fill['usd_volume'], fill['price']))
        return float(fill['price']), float(fill['usd_volume']), float(fill['size']), float(fill['fee'])

    def placeLimitOrder(self, product_id, side, price, size):
        result = self.client.place_limit_order(product_id=product_id, side=side, price=price, size=size)
        logging.info('[API] result: ' + str(result))
        logging.info('[{}] Created {} order for price {}'.format(side.upper(), size, price))
        return result['id']

    def checkIfOrdersFilled(self, orderids):
        completedFills=[]
        for order in orderids:
            fills = list(self.client.get_fills(order_id=order))
            if len(fills) == 1:
                completedFills.append(fills[1])
        return completedFills

    def getFees(self):
        result = self.client.get_fees()
        logging.info('[GETFEES] result ' + str(result))
        return float(result['taker_fee_rate'])

    def _getOrderDetails(self, orderid):
        fills = []
        while len(fills) == 0:
            time.sleep(2)
            logging.info('[FILL] Looking for orderid ' + orderid)
            result = self.client.get_fills(order_id=orderid)
            fills = list(result)
        return fills[0]
