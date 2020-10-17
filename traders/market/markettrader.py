import sys
import logging
from datamanager import DataManager
from cpapi import CbApi
from libs.authenticated_client import AuthenticatedClient
from traders.trader import Trader

class MarketTrader(Trader):
    def __init__(self, productid, cashaccount, cryptoaccount):
        super().__init__(productid, cashaccount, cryptoaccount, 'traders/market/marketlog.log', 'traders/market/marketdata.json')

        self.isInBuyState = True
        self.lastOpPrice = 0.00
        self.data = self.dm.loadData()

        lastOp = {} if len(self.data)==0 else self.data[-1]
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

    def attemptToMakeTrade(self):
        try:
            currentPrice = self.api.getMarketPrice(self.product_id)
            if self.lastOpPrice==0:
                self._updateOpPrice(currentPrice)
                return
            difference = currentPrice - self.lastOpPrice
            percentDiff = difference/self.lastOpPrice*100
            logging.info('[CHECK][{}] {} - {} = {} {}%'.format('BUY' if self.isInBuyState else 'SELL', currentPrice, self.lastOpPrice, round(difference,2), round(percentDiff,2)))
            if (self.isInBuyState):
                self._tryToBuy(percentDiff)
            else:
                self._tryToSell(percentDiff)
        except Exception as e:
            logging.info('[ERROR] ' + repr(e))

    def _tryToBuy(self, percentDiff):
        if percentDiff >= self.Upward_Trend_Threshold or percentDiff <= self.Dip_Threshold:
            self._updateOpPrice(self._placeMarketBuyOrder())
            self.isInBuyState = False

    def _tryToSell(self, percentDiff):
        if percentDiff >= self.Profit_Threshold or percentDiff <= self.Stop_Loss_Threshold:
            self._updateOpPrice(self._placeMarketSellOrder())
            self.isInBuyState = True

    def _placeMarketBuyOrder(self):
        account = self.api.getAccountDetails(self.cash_account_id)
        fundsToUse = round(float(account['balance']) * 0.5, 2)
        newPrice = self.api.placeMarketOrder(self.product_id, 'buy', funds=fundsToUse)
        self._addOperation({ 'operation': 'buy', 'lastOpPrice': newPrice })
        return newPrice

    def _placeMarketSellOrder(self):
        account = self.api.getAccountDetails(self.crypto_account_id)
        amountToSell = float(account['balance'])
        newPrice = self.api.placeMarketOrder(self.product_id, 'sell', size=amountToSell)
        self._addOperation({ 'operation': 'sell', 'lastOpPrice': newPrice })
        return newPrice

    def _updateOpPrice(self, newprice):
        logging.info('[UPDATE] lastOpPrice: ' + str(self.lastOpPrice) + ' to ' + str(newprice))
        self.lastOpPrice = newprice

    def _addOperation(self,operation):
        self.data.append(operation)
        self.dm.saveData(self.data)