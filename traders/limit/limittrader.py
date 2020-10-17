import logging
from cpapi import CbApi
from datamanager import DataManager
from traders.trader import Trader

class LimitTrader(Trader):
    def __init(self, productid, cashaccount, cryptoaccount):
        super().__init__(productid, cashaccount, cryptoaccount, 'traders/limit/log.log', 'traders/limit/data.json')

        self.data = self.dm.loadData()
        self.lastOperation = {} if len(self.data) else self.data[-1]
        if 'operation' not in self.lastOperation:
            self.lastOperation['operation'] = 'buy'
        if 'price' not in self.lastOperation:
            self.lastOperation['price'] = 0
        
        self.Upward_Trend_Threshold = 1.5
        self.Dip_Threshold = -2.25

        self.Profit_Threshold = 1.25
        self.Stop_Loss_Threshold = -2.00

    def attemptToMakeLimitTrade(self):
        try:
            if self.lastOperation['price'] == 0:
                self.lastOperation['price'] = self.api.getMarketPrice(self.product_id)
            if len(self.lastOperation['orders']) == 0:
                self.createLimitOrders()
            fills = self.api.checkIfOrdersFilled(self.lastOperation['orders'])
            if len(fills) == 1:
                operation = 'sell' if fills[0]['side'] == 'buy' else 'buy'
                self.updateLastOperation({ 'operation': operation, 'price': float(fills[0]['price']) })
                # self.updateOpPrice(float(fills[0]['price']))
                # self.isInBuyState = fills[0]['side'] == 'sell'
                # self.orderIds = []
        except Exception as e:
            logging.info('[ERROR] ' + repr(e))
    
    def createLimitOrders(self):
        lastPrice = self.lastOperation['price']
        isInBuyState = self.lastOperation['operation']
        maxlimit = (self.Upward_Trend_Threshold if isInBuyState else self.Profit_Threshold)/100
        minlimit = (self.Dip_Threshold if isInBuyState else self.Stop_Loss_Threshold)/100
        maxPrice = round(lastPrice + (lastPrice * maxlimit), 2)
        minPrice = round(lastPrice + (lastPrice * minlimit), 2)
        if isInBuyState:
            account = self.api.getAccountDetails(self.cash_account_id)
            funds = round(float(account['balance']) * 0.5, 2)
            size = funds / maxPrice
        else:
            account = self.api.getAccountDetails(self.crypto_account_id)
            size = float(account['balance'])
        side = 'buy' if isInBuyState else 'sell'
        self.lastOperation['orders'].append(self.api.placeLimitOrder(self.product_id, side, maxPrice, size))
        self.lastOperation['orders'].append(self.api.placeLimitOrder(self.product_id, side, minPrice, size))
        # self.dm.addOperation(side, self.lastOpPrice, self.orderIds)
        # self.dm.save()

    def updateLastOperation(self, operation):
        logging.info('[UPDATE] previous: ' + str(self.lastOperation))
        logging.info('[UPDATE] updated : ' + str(operation))
        self.lastOperation = operation
        self.dm.saveData(self.data)