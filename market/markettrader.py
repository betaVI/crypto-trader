import sys
import logging
from datamanager import DataManager
from cpapi import CbApi
from libs.authenticated_client import AuthenticatedClient

class MarketTrader:
    def __init__(self):
        logging.basicConfig(level=logging.INFO, filename='logs/marketlog.log', format='%(asctime)s - %(message)s', datefmt='%m-%d-%Y %H:%M:%S')
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console.setFormatter(logging.Formatter(fmt='%(asctime)s - %(message)s', datefmt='%m-%d-%Y %H:%M:%S'))
        logging.getLogger().addHandler(console)
        logging.info("Start")

        self.api = CbApi()
        self.dm = DataManager('market/marketdata.json')

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

    # def attemptToMakeLimitTrade(self):
    #     try:
    #         if self.lastOpPrice == 0:
    #             self.updateOpPrice(self.api.getMarketPrice(self.product_id))
    #         if len(self.orderIds) == 0:
    #             self.createLimitOrders()
    #         fills = self.api.checkIfOrdersFilled(self.orderIds)
    #         if len(fills) == 1:
    #             self.updateOpPrice(float(fills[0]['price']))
    #             self.isInBuyState = fills[0]['side'] == 'sell'
    #             self.orderIds = []
    #     except Exception as e:
    #         logging.info('[ERROR] ' + repr(e))

    # def createLimitOrders(self):
    #     maxlimit = (self.Upward_Trend_Threshold if self.isInBuyState else self.Profit_Threshold)/100
    #     minlimit = (self.Dip_Threshold if self.isInBuyState else self.Stop_Loss_Threshold)/100
    #     maxPrice = round(self.lastOpPrice + (self.lastOpPrice * maxlimit), 2)
    #     minPrice = round(self.lastOpPrice + (self.lastOpPrice * minlimit), 2)
    #     if self.isInBuyState:
    #         account = self.api.getAccountDetails(self.cash_account_id)
    #         funds = round(float(account['balance']) * 0.5, 2)
    #         size = funds / maxPrice
    #     else:
    #         account = self.api.getAccountDetails(self.crypto_account_id)
    #         size = float(account['balance'])
    #     side = 'buy' if self.isInBuyState else 'sell'
    #     self.orderIds.append(self.api.placeLimitOrder(self.product_id, side, maxPrice, size))
    #     self.orderIds.append(self.api.placeLimitOrder(self.product_id, side, minPrice, size))
    #     # self.dm.addOperation(side, self.lastOpPrice, self.orderIds)
    #     # self.dm.save()

    def attemptToMakeMarketTrade(self):
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
            self.updateOpPrice(self.placeMarketBuyOrder())
            self.isInBuyState = False

    def tryToSell(self, percentDiff):
        if percentDiff >= self.Profit_Threshold or percentDiff <= self.Stop_Loss_Threshold:
            self.updateOpPrice(self.placeMarketSellOrder())
            self.isInBuyState = True

    def placeMarketBuyOrder(self):
        account = self.api.getAccountDetails(self.cash_account_id)
        fundsToUse = round(float(account['balance']) * 0.5, 2)
        newPrice = self.api.buy(self.product_id, fundsToUse)
        self.dm.addOperation({ 'operation': 'buy', 'lastOpPrice': newPrice })
        return newPrice

    def placeMarketSellOrder(self):
        account = self.api.getAccountDetails(self.crypto_account_id)
        amountToSell = float(account['balance'])
        newPrice = self.api.sell(self.product_id, amountToSell)
        self.dm.addOperation({ 'operation': 'sell', 'lastOpPrice': newPrice })
        return newPrice

    def updateOpPrice(self, newprice):
        logging.info('[UPDATE] lastOpPrice: ' + str(self.lastOpPrice) + ' to ' + str(newprice))
        self.lastOpPrice = newprice