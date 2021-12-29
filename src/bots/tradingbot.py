import sys
import signal
import time
import os
from bots.traders.market.markettrader import MarketTrader
from bots.traders.average.averagetrader import AverageTrader

def handle_cancel(sig, frame):
    print('Cancelled')
    sys.exit(0)

if __name__ == "__main__":
    print('cwd is %s' %(os.getcwd()))
    signal.signal(signal.SIGINT, handle_cancel)
    runinterval = 5
    productid = 'BTC-USD'
    cash_account_id = 'xxxxxxxxxxxxxxxxxxxxxxxxx'
    crypto_account_id = 'xxxxxxxxxxxxxxxxxxxxxxx'

    trader = AverageTrader(productid, cash_account_id, crypto_account_id)
    # trader = MarketTrader(productid, cash_account_id, crypto_account_id)
    while True:
        trader.attemptToMakeTrade()
        print('Waiting ' + str(runinterval) + ' seconds')
        time.sleep(runinterval)