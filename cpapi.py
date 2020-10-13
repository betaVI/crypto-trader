import time
import logging
from libs.authenticated_client import AuthenticatedClient

class CbApi:
    def __init__(self):
        
        key = 'xxxxxxxxxxxxxxxxx'
        b64secret = 'xxxxxxxxxxxxxxxxxxxxxx=='
        passphrase = 'xxxxxxxxxxxx'
        url = 'https://api-public.sandbox.pro.coinbase.com'
        self.client = AuthenticatedClient(key, b64secret, passphrase, api_url=url)
        
    def getAccountDetails(self, account_id):
        account = self.client.get_account(account_id)
        logging.info('[BALANCE] ' + account['currency'] + ': ' + str(account['balance']))
        return account

    def getMarketPrice(self, product_id):
        result = self.client.get_product_ticker(product_id)
        # logging.info('[PRICE] ' + product_id + ' ' + str(result['price']))
        return float(result['price'])

    def buy(self, product_id, funds):
        result = self.client.place_market_order(product_id=product_id, side='buy', funds=funds)
        orderid = result['id']
        fill = self.getOrderDetails(orderid)
        logging.info('[BUY] Used ' + str(funds) +' to buy ' + str(fill['size']) + ' at ' + str(fill['price']))
        return float(fill['price'])

    def sell(self, product_id, size):
        result = self.client.place_market_order(product_id=product_id, side='sell', size=size)
        orderid = result['id']
        fill = self.getOrderDetails(orderid)
        logging.info('[SELL] Sold ' + str(size) + ' for ' + str(fill['usd_volume']) + ' at ' + str(fill['price']))
        return float(fill['price'])

    def placeLimitOrder(self, product_id, side, price, size):
        result = self.client.place_limit_order(product_id=product_id, side=side, price=price, size=size)
        logging.info('[API] result: ' + str(result))
        logging.info('[{}] Created {} order for price {}'.format(side.upper(), size, price))
        return result['id']

    def getOrderDetails(self, orderid):
        fills = []
        while len(fills) == 0:
            time.sleep(2)
            logging.info('[FILL] Looking for orderid ' + orderid)
            result = self.client.get_fills(order_id=orderid)
            fills = list(result)
        return fills[0]

    def checkIfOrdersFilled(self, orderids):
        completedFills=[]
        for order in orderids:
            fills = list(self.client.get_fills(order_id=order))
            if len(fills) == 1:
                completedFills.append(fills[1])
        return completedFills
