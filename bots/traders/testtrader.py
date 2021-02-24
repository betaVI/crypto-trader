import logging, traceback
import numpy as np
from bots.traders.trader import Trader
from bots.dbloghandler import DbLogHandler

class TestTrader():
    def __init__(self, dbtrader, api, dbloghandler):
        self.cash_account_id = dbtrader['quoteaccount']
        self.crypto_account_id = dbtrader['baseaccount']
        self.product_id = dbtrader['product']
        self.api = api
        self.log = logging.getLogger(self.product_id)
        self.log.setLevel(logging.DEBUG)

        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console.setFormatter(logging.Formatter(fmt='%(asctime)s - %(message)s', datefmt='%m-%d-%Y %H:%M:%S'))

        self.log.info("Start")

    def attemptToMakeTrade(self):
        try:
            length = len(self.state['orders'])
            if length == 0:
                self._placeBuyOrder()
            else:
                marketPrice = self.api.getMarketPrice(self.product_id)
                if self.lastMarketPrice==0:
                    self.lastMarketPrice = marketPrice
                avgPrice = self._getAveragePricePaid()
                difference = marketPrice - avgPrice
                percentDiff = difference/avgPrice*100
                profitMargin = self._getProfitMargin()
                maxAmount = avgPrice + (avgPrice * profitMargin) / 100
                minAmount = avgPrice + (avgPrice * self.Dip_Threshold) / 100
                self.log.info('[CHECK] {} - {} = {} {}% (MAX: {} | MIN: {})'.format(marketPrice, avgPrice, round(difference,2), round(percentDiff,2), round(maxAmount,2), round(minAmount,2)))
                # logging.info('[PROFITMARGIN] ' +str(profitMargin))
                if percentDiff <= self.Dip_Threshold:
                    isStable = self._isPriceStable(marketPrice, 'buy')
                    if isStable:
                        self._placeBuyOrder()
                elif percentDiff >= profitMargin:
                    isStable = self._isPriceStable(marketPrice, 'sell')
                    if isStable:
                        self._placeSellOrder()
                self.lastMarketPrice = marketPrice
        except Exception: # as e:
            self.log.exception(traceback.format_exc())

    def _isPriceStable(self, marketPrice, side):
        trades = self.api.getRecentTrades(self.product_id, side, 40)
        avgTradePrice = np.mean(trades)
        standardDeviation = np.std(trades)
        highStd = round(avgTradePrice + standardDeviation,2)
        lowStd = round(avgTradePrice - standardDeviation,2)
        isstable = lowStd <= marketPrice and marketPrice <= highStd
        return isstable

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
        return round(sum([o['funds'] for o in self.state['orders']])/sum([o['size'] for o in self.state['orders']]), 2)

    def _getProfitMargin(self):
        return (self.state['fee'] * 100) * len(self.state['orders']) + self.Profit_Threshold
        
    def _updateFees(self):
        fee = self.api.getFees()
        if 'fee' not in self.state:
            self.log.info('[FEE] Set to {}'.format(fee))
        elif fee != self.state['fee']:
            self.log.info('[FEE] Updated from {} to {}'.format(self.state['fee'], fee))
        self.state['fee'] = fee