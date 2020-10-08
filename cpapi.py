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
        logging.info('[API] result: ' + str(result))
        logging.info('[BUY] Bought ' + str(result['size']) + ' for ' + str(funds))
        return float(result['price'])

    def sell(self, product_id, size):
        result = self.client.place_market_order(product_id=product_id, side='sell', size=size)
        logging.info('[API] result: ' + str(result))
        logging.info('[SELL] Sold ' + str(result['size']))
        return float(result['price'])