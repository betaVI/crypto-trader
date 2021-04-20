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
        self.totalSpent = float(dbtrader['totalspent'])
        self.Dip_Threshold = float(dbtrader['buylowerthreshold'])
        self.Profit_Threshold = float(dbtrader['sellupperthreshold'])
        self.cashout = dbtrader['status'] == 'Cash Out'
        self.api = api
        self.orderrepo = orderrepo

        self.log = logging.getLogger(self.product_id)
        self.log.setLevel(logging.DEBUG)

        self._updateFees()

        self.group = orderrepo.fetchRecentOrderGroup(self.product_id)
        if self.group == None:
            self.group = orderrepo.createOrderGroup(self.product_id)

        self.log.debug("Start")

    def attemptToMakeTrade(self):
        try:
            length = len(self.group['orders'])
            if length == 0:
                self.log.info('Placing Buy Order because none were found')
                self._placeBuyOrder()
            elif self.maxPurchaseAmount-self.totalSpent <= 0:
                self.log.warn('[BALANCE] NSF {} - {} = {}'.format(self.maxPurchaseAmount, self.totalSpent, self.maxPurchaseAmount - self.totalSpent))
            elif self.cashout:
                self.log.info('[CASH OUT]')
                self._placeSellOrder()
            else:
                marketPrice = self.api.getMarketPrice(self.product_id)
                avgPrice = self._getAveragePricePaid()
                differenceMax = marketPrice - avgPrice
                percentDiffMax = differenceMax/avgPrice*100
                lastpurchaseprice = self._getLastPurchasePrice()
                differenceMin = marketPrice - lastpurchaseprice
                percentDiffMin = differenceMin/lastpurchaseprice*100
                profitMargin = self._getProfitMargin()
                # logging.info('[PROFITMARGIN] ' +str(profitMargin))
                maxAmount = avgPrice + (avgPrice * profitMargin) / 100
                minAmount = lastpurchaseprice + (lastpurchaseprice * self.Dip_Threshold) / 100
                self.log.debug('[CHECK MAX] {} - {} = {} {}% {}'.format(marketPrice, avgPrice, round(differenceMax,2), round(percentDiffMax,2), round(maxAmount,2)))
                self.log.debug('[CHECK MIN] {} - {} = {} {}% {}'.format(marketPrice, lastpurchaseprice, round(differenceMin,2), round(percentDiffMin,2), round(minAmount,2)))
                if percentDiffMin <= self.Dip_Threshold:
                    isStable = self._isPriceStable(marketPrice, 'buy')
                    if isStable:
                        self._placeBuyOrder()
                elif percentDiffMax >= profitMargin:
                    isStable = self._isPriceStable(marketPrice, 'sell')
                    if isStable:
                        self._placeSellOrder()
            self.log.debug("Finished")
            return True
        except Exception: # as e:
            self.log.critical(traceback.format_exc())
            return False

    def _isPriceStable(self, marketPrice, side):
        self.log.debug("Checking price stability")
        trades = self.api.getRecentTrades(self.product_id, side, 40)
        avgTradePrice = np.mean(trades)
        standardDeviation = np.std(trades)
        highStd = round(avgTradePrice + standardDeviation,5)
        lowStd = round(avgTradePrice - standardDeviation,5)
        isstable = lowStd <= marketPrice and marketPrice <= highStd
        self.log.debug('[{}] AVG: {} | STD: {} | HIGH: {} | LOW: {}'.format("STABLE" if isstable else "UNSTABLE", avgTradePrice, standardDeviation, highStd, lowStd))
        return isstable

    def _placeBuyOrder(self):
        self.log.debug("Attempting to place a Buy Order")
        remainingbalance = self.maxPurchaseAmount - self.totalSpent
        fundsToUse = round(max(remainingbalance * 0.5, 0.5), 2)
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
        # self.orderrepo.createOrder(self.group['id'], 'sell', funds, id, size, price, fee)
        self.orderrepo.updateOrderGroup(id, self.group['id'], price, funds, size, fee)
        self.group = self.orderrepo.createOrderGroup(self.product_id)
        self._updateFees()
        return price

    def _getLastPurchasePrice(self):
        return min([float(o['price']) for o in self.group['orders']])

    def _getAveragePricePaid(self):
        return round(sum([float(o['funds']) for o in self.group['orders']])/sum([float(o['size']) for o in self.group['orders']]), 2)

    def _getProfitMargin(self):
        return (self.fee * 100) * len(self.group['orders']) + self.Profit_Threshold

    def _updateFees(self):
        self.fee = self.api.getFees()