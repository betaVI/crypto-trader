import logging, time
from src.services.cpapi import CbApi
from coinbase.rest import RESTClient

class LiveCbApi(CbApi):
    def __init__(self, api_key, api_secret):
        self.logger = logging.getLogger('CPAPI')
        self.logger.setLevel(logging.DEBUG)
        self.client = RESTClient(api_key=api_key, api_secret=api_secret)

    def getProducts(self):
        response = self.client.get_products()
        products = []
        for product in response['products']:
            product['id'] = product['product_id']
            products.append(product)
        return products
    
    def getProduct(self, product_id):
        product = self.client.get_product(product_id)
        return product#['base_increment']
    
    def getAccounts(self):
        response = self.client.get_accounts()
        return response.accounts
    
    def getAccountDetails(self, account_id):
        account = self.client.get_account(account_id)
        return account
    
    def getMarketPrice(self, product_id):
        result = self.client.get_product(product_id)
        self.logger.info('[GET MARKET PRICE RESULT] ' + product_id + ' ' + str(result))
        return float(result['price'])
    
    def getRecentTrades(self, product_id, side, count):
        response = self.client.get_public_market_trades(product_id, limit=count)
        return [float(t['price']) for t in response['trades']]
    
    def placeMarketOrder(self, product_id, side, funds=None, size=None):
        # funds = amount to use to buy
        # size = amount to sell
        # quote_size  = amount of quote currency to spend BUY ONLY
        # base_size = amount of base currency to spend
        # BTC-USD = BTC is base, USD is qoute

        # result = self.client.place_market_order(product_id=product_id, side=side, size=size, funds=funds)
        result = self.client.market_order(product_id=product_id, side=side, base_size=size, quote_size=funds)

        logging.getLogger(product_id).debug('[API] Market Order Result: ' + str(result))
        orderid = result['id']
        fill = self._getOrderDetails(orderid)
        return orderid, float(fill['price']), float(fill['usd_volume']), float(fill['size']), float(fill['fee'])
    
    def getFees(self):
        result = self.client.get_transaction_summary()
        self.logger.info('[GETFEES] result ' + str(result))
        return float(result['fee_tier']['taker_fee_rate'])
    
    def _getOrderDetails(self, orderid):
        fills = []
        while len(fills) == 0:
            time.sleep(2)
            self.logger.info('[FILL] Looking for orderid ' + orderid)
            result = self.client.get_fills(order_id=orderid)
            fills = list(result)
        return fills[0]