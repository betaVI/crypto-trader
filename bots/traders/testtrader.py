import logging, traceback
import numpy as np
from bots.traders.trader import Trader
from bots.dbloghandler import DbLogHandler

class TestTrader():
    def __init__(self, orderrepo, dbtrader, api):
        self.cash_account_id = dbtrader['quoteaccount']
        self.crypto_account_id = dbtrader['baseaccount']
        self.product_id = dbtrader['product']
        self.maxPurchaseAmount = float(dbtrader['maxpurchaseamount'])
        self.Dip_Threshold = float(dbtrader['buylowerthreshold'])
        self.Profit_Threshold = float(dbtrader['sellupperthreshold'])
        self.api = api
        self.orderrepo = orderrepo

        self.log = logging.getLogger(self.product_id)
        self.log.setLevel(logging.DEBUG)

        self._updateFees()

        self.group = orderrepo.fetchRecentOrderGroup(self.product_id)
        if self.group == None:
            self.group = orderrepo.createOrderGroup(self.product_id)

        self.log.info("Start")

    def attemptToMakeTrade(self):
        try:
            length = len(self.group['orders'])
            if length == 0:
                self.log.info('Placing Buy Order because non were found')
                self._placeBuyOrder()
            else:
                marketPrice = self.api.getMarketPrice(self.product_id)
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
            self.log.info("Finished")
        except Exception: # as e:
            self.log.exception(traceback.format_exc())

    def _isPriceStable(self, marketPrice, side):
        self.log.debug("Checking price stability")
        trades = self.api.getRecentTrades(self.product_id, side, 40)
        avgTradePrice = np.mean(trades)
        standardDeviation = np.std(trades)
        highStd = round(avgTradePrice + standardDeviation,5)
        lowStd = round(avgTradePrice - standardDeviation,5)
        isstable = lowStd <= marketPrice and marketPrice <= highStd
        self.log.info('[{}] AVG: {} | STD: {} | HIGH: {} | LOW: {}'.format("STABLE" if isstable else "UNSTABLE", avgTradePrice, standardDeviation, highStd, lowStd))
        return isstable

    def _placeBuyOrder(self):
        self.log.debug("Attempting to place a Buy Order")
        totalspent = self._getTotalSpent()
        if self.maxPurchaseAmount - totalspent<0:
            self.log.info('[BALANCE] NSF {} - {} = {}'.format(self.maxPurchaseAmount, totalspent, self.maxPurchaseAmount - totalspent))
            return
        remainingbalance = max(self.maxPurchaseAmount - totalspent,.5)
        fundsToUse = round(remainingbalance * 0.5, 2)
        id, price, funds, size, fee = self.api.placeMarketOrder(self.product_id, 'buy', funds=fundsToUse)
        self.log.info('[BUY] {} {} for ${} at {}/{}'.format(size, self.product_id, funds, price, self.product_id))
        self.orderrepo.createOrder(self.group['id'], 'buy', funds, id, size, price, fee)
        self._updateFees()

    def _placeSellOrder(self):
        self.log.debug("Attempting to place a Sell Order")
        account = self.api.getAccountDetails(self.crypto_account_id)
        amountToSell = float(account['balance'])
        id, price, funds, size, fee = self.api.placeMarketOrder(self.product_id, 'sell', size=amountToSell)
        self.log.info('[SELL] {} {} for ${} at {}/{}'.format(size, self.product_id, funds, price, self.product_id))
        # self.dm.addOperation({ 'operation': 'sell', 'lastOpPrice': newPrice })
        # totalfees = sum([o['fee'] for o in self.state['orders']]) + fee
        self.orderrepo.createOrder(self.group['id'], 'sell', funds, id, size, price, fee)
        self.orderrepo.updateOrderGroup(self.group['id'], funds, size, fee)
        self.group = self.orderrepo.createOrderGroup(self.product_id)
        self._updateFees()
        return price

    def _getAveragePricePaid(self):
        return round(sum([float(o['funds']) for o in self.group['orders']])/sum([float(o['size']) for o in self.group['orders']]), 2)

    def _getTotalSpent(self):
        return round(sum([float(o['funds']) for o in self.group['orders'] if o['side']=='buy']))

    def _getProfitMargin(self):
        return (self.fee * 100) * len(self.group['orders']) + self.Profit_Threshold

    def _updateFees(self):
        self.fee = self.api.getFees()