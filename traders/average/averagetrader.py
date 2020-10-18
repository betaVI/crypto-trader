import logging
import traceback
import numpy as np
from traders.trader import Trader

class AverageTrader(Trader):
    def __init__(self, productid, cashaccount, cryptaccount):
        super().__init__(productid, cashaccount, cryptaccount, 'traders/average/averagelog.log','traders/average/averagedata.json')

        self.lastMarketPrice = 0
        self.data = self.dm.loadData()

        if len(self.data) ==0:
            self.data.append({})
        self.state = self.data[-1]

        if 'orders' not in self.state:
            self.state['orders'] = []

        # fill = self.api._getOrderDetails('44f8d18b-9a9e-4731-b17c-33759ddcd05c')
        # print(fill)

        self._updateFees()
        self._updateState()

        self.Upward_Trend_Threshold = 1.5
        self.Dip_Threshold = -2.25

        self.Profit_Threshold = 1.25
        self.Stop_Loss_Threshold = -2.00

    def attemptToMakeTrade(self):
        try:
            if len(self.state['orders']) == 0:
                self._placeBuyOrder()
            else:
                marketPrice = self.api.getMarketPrice(self.product_id)
                if self.lastMarketPrice==0:
                    self.lastMarketPrice = marketPrice
                avgPrice = self._getAveragePricePaid()
                difference = marketPrice - avgPrice
                percentDiff = difference/avgPrice*100
                logging.info('[CHECK] {} - {} = {} {}%'.format(marketPrice, avgPrice, round(difference,2), round(percentDiff,2)))
                profitMargin = self._getProfitMargin()
                logging.info('[PROFITMARGIN] ' +str(profitMargin))
                lastPriceDiff = ((marketPrice - self.lastMarketPrice)/self.lastMarketPrice)*100
                if percentDiff <= self.Dip_Threshold:
                    self._placeBuyOrder()
                elif percentDiff >= profitMargin and lastPriceDiff < 4.00:
                    self._placeSellOrder()
                self.lastMarketPrice = marketPrice
        except Exception: # as e:
            logging.exception(traceback.format_exc())

    def _placeBuyOrder(self):
        account = self.api.getAccountDetails(self.cash_account_id)
        fundsToUse = round(float(account['balance']) * 0.5, 2)
        price, funds, size, fee = self.api.placeMarketOrder(self.product_id, 'buy', funds=fundsToUse)
        self.state['orders'].append({
            'price': price,
            'funds': funds,
            'size': size,
            'fee': fee
        })
        self._updateFees()
        self._updateState()
        return price

    def _placeSellOrder(self):
        account = self.api.getAccountDetails(self.crypto_account_id)
        amountToSell = float(account['balance'])
        price, funds, size, fee = self.api.placeMarketOrder(self.product_id, 'sell', size=amountToSell)
        # self.dm.addOperation({ 'operation': 'sell', 'lastOpPrice': newPrice })
        # totalfees = sum([o['fee'] for o in self.state['orders']]) + fee
        totalspent = sum([o['funds'] + o['fee'] for o in self.state['orders']])
        self.state['fundsearned'] = funds
        self.state['totalspent'] = totalspent
        self.state['totalearned'] = funds - fee
        self.state['profit'] = (funds - fee) - totalspent
        self.state['sizesold'] = size
        self.state['feespaid'] = fee
        self._addState()
        return price

    def _getAveragePricePaid(self):
        return sum([o['funds'] for o in self.state['orders']])/sum([o['size'] for o in self.state['orders']])

    def _getProfitMargin(self):
        return (self.state['fee'] * 100) * len(self.state['orders']) + self.Profit_Threshold
        
    def _updateFees(self):
        fee = self.api.getFees()
        if 'fee' not in self.state:
            logging.info('[FEE] Set to {}'.format(fee))
        elif fee != self.state['fee']:
            logging.info('[FEE] Updated from {} to {}'.format(self.state['fee'], fee))
        self.state['fee'] = fee

    def _addState(self):
        self.data[-1] = self.state
        self.state = {
            'orders':[]
        }
        self._updateFees()
        self.data.append(self.state)
        self.dm.saveData(self.data)

    def _updateState(self):
        self.data[-1] = self.state
        self.dm.saveData(self.data)
