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
        logging.info('[BALANCE] {}: {}'.format(account['currency'], account['balance']))
        return account

    def getMarketPrice(self, product_id):
        result = self.client.get_product_ticker(product_id)
        # logging.info('[PRICE] ' + product_id + ' ' + str(result['price']))
        return float(result['price'])

    def placeMarketOrder(self, product_id, side, funds = None, size = None):
        result = self.client.place_market_order(product_id=product_id, side=side, size=size, funds=funds)
        orderid = result['id']
        fill = self._getOrderDetails(orderid)
        logging.info('[{}] {} BTC for ${} at {}/BTC'.format(side.upper(), fill['size'], fill['usd_volume'], fill['price']))
        return float(fill['price']), round(float(fill['usd_volume']),2), float(fill['size']), round(float(fill['fee']),2)

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
