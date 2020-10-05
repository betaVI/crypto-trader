import logging
from libs.authenticated_client import AuthenticatedClient

class Trader:
    def __init__(self):
        logging.basicConfig(level=logging.INFO, filename='testlog.log', format='%(asctime)s - %(message)s', datefmt='%m-%d-%Y %H:%M:%S')
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console.setFormatter(logging.Formatter(fmt='%(asctime)s - %(message)s', datefmt='%m-%d-%Y %H:%M:%S'))
        logging.getLogger().addHandler(console)
        logging.info("Start")

        self.isInBuyState = True

        self.Upward_Trend_Threshold = 1.5
        self.Dip_Threshold = -2.25
        self.Profit_Threshold = 1.25
        self.Stop_Loss_Threshold = -2.00

        self.lastOpPrice = 0.00
        
        self.cash_account_id = 'xxxxxxxxxxxxxxxxxxxxxxxxx'
        self.crypto_account_id = 'xxxxxxxxxxxxxxxxxxxxxxx'
        #self.product_id = 'LTC-USD'
        self.product_id = 'BTC-USD'

        key = 'xxxxxxxxxxxxxxxxx'
        b64secret = 'xxxxxxxxxxxxxxxxxxxxxx=='
        passphrase = 'xxxxxxxxxxxx'
        url = 'https://api-public.sandbox.pro.coinbase.com'
        self.client = AuthenticatedClient(key, b64secret, passphrase, api_url=url)

    def attemptToMakeTrade(self):
        currentPrice = self.getMarketPrice()
        if self.lastOpPrice==0:
            self.updateOpPrice(currentPrice)
            return
        difference = currentPrice - self.lastOpPrice
        percentDiff = difference/self.lastOpPrice*100
        logging.info('[CHECK] ' + str(currentPrice) + ' - ' + str(self.lastOpPrice) + ' = ' + str(round(difference,2)) + ' ' + str(round(percentDiff,2)) + '%')
        if (self.isInBuyState):
            self.tryToBuy(percentDiff)
        else:
            self.tryToSell(percentDiff)

    def tryToBuy(self, percentDiff):
        if percentDiff >= self.Upward_Trend_Threshold or percentDiff <= self.Dip_Threshold:
            self.updateOpPrice(self.placeBuyOrder())
            self.isInBuyState = False

    def tryToSell(self, percentDiff):
        if percentDiff >= self.Profit_Threshold or percentDiff <= self.Stop_Loss_Threshold:
            self.updateOpPrice(self.placeSellOrder())
            self.isInBuyState = True

    def getCashAccount(self):
        account = self.client.get_account(self.cash_account_id)
        logging.info('[BALANCE] ' + account['currency'] + ': ' + str(account['balance']))
        return account

    def getCryptoAccount(self):
        account = self.client.get_account(self.crypto_account_id)
        logging.info('[BALANCE] ' + account['currency'] + ': ' + str(account['balance']))
        return account

    def getMarketPrice(self):
        result = self.client.get_product_ticker(self.product_id)
        logging.info('[PRICE] ' + self.product_id + ' ' + str(result['price']))
        return float(result['price'])

    def placeBuyOrder(self):
        account = self.getCashAccount()
        fundsToUse = account['balance'] * 0.25
        result = self.client.place_market_order(product_id=self.product_id, side='buy', funds=fundsToUse)
        logging.info('[BUY] Bought ' + str(result['size']) + ' for ' + str(result['price']))
        return result['price']

    def placeSellOrder(self):
        account = self.getCryptoAccount()
        amountToSell = account['balance'] * 0.25
        result = self.client.place_market_order(product_id=self.product_id, side='sell', size=amountToSell)
        logging.info('[SELL] Sold ' + str(result['size']) + ' for ' + str(result['price']))
        return result['price']

    def updateOpPrice(self, newprice):
        logging.info('[UPDATE] lastOpPrice: ' + str(self.lastOpPrice) + ' to ' + str(newprice))
        self.lastOpPrice = newprice