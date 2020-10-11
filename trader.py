import sys
import logging
from datamanager import DataManager
from cpapi import CbApi
from libs.authenticated_client import AuthenticatedClient

class Trader:
    def __init__(self):
        logging.basicConfig(level=logging.INFO, filename='logs/testlog.log', format='%(asctime)s - %(message)s', datefmt='%m-%d-%Y %H:%M:%S')
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console.setFormatter(logging.Formatter(fmt='%(asctime)s - %(message)s', datefmt='%m-%d-%Y %H:%M:%S'))
        logging.getLogger().addHandler(console)
        logging.info("Start")

        self.api = CbApi()
        self.dm = DataManager()

        self.isInBuyState = True
        self.lastOpPrice = 0.00

        lastOp = self.dm.lastOpResults()
        if 'operation' in lastOp:
            self.isInBuyState = False if lastOp['operation'] == 'buy' else True
        if 'lastOpPrice' in lastOp:
            self.lastOpPrice = float(lastOp['lastOpPrice'])

        self.Upward_Trend_Threshold = 1.5
        self.Dip_Threshold = -2.25

        self.Profit_Threshold = 1.25
        self.Stop_Loss_Threshold = -2.00

        # orders = self.api.getOrderDetails('cb27dc70-1e6f-4243-8bd4-791cad47d02a')
        # logging.info("[ORDER] Info: " + str(orders))
        
        self.cash_account_id = 'xxxxxxxxxxxxxxxxxxxxxxxxx'
        self.crypto_account_id = 'xxxxxxxxxxxxxxxxxxxxxxx'
        #self.product_id = 'LTC-USD'
        self.product_id = 'BTC-USD'

    def attemptToMakeTrade(self):
        try:
            currentPrice = self.api.getMarketPrice(self.product_id)
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
        except Exception as e:
            logging.info('[ERROR] ' + repr(e))

    def tryToBuy(self, percentDiff):
        if percentDiff >= self.Upward_Trend_Threshold or percentDiff <= self.Dip_Threshold:
            self.updateOpPrice(self.placeBuyOrder())
            self.isInBuyState = False

    def tryToSell(self, percentDiff):
        if percentDiff >= self.Profit_Threshold or percentDiff <= self.Stop_Loss_Threshold:
            self.updateOpPrice(self.placeSellOrder())
            self.isInBuyState = True

    def placeBuyOrder(self):
        account = self.api.getAccountDetails(self.cash_account_id)
        fundsToUse = round(float(account['balance']) * 0.5, 2)
        newPrice = self.api.buy(self.product_id, fundsToUse)
        self.dm.addOperation('buy', newPrice)
        return newPrice

    def placeSellOrder(self):
        account = self.api.getAccountDetails(self.crypto_account_id)
        amountToSell = float(account['balance'])
        newPrice = self.api.sell(self.product_id, amountToSell)
        self.dm.addOperation('sell', newPrice)
        return newPrice

    def updateOpPrice(self, newprice):
        logging.info('[UPDATE] lastOpPrice: ' + str(self.lastOpPrice) + ' to ' + str(newprice))
        self.lastOpPrice = newprice