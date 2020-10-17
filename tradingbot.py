import sys
import signal
import time
from traders.market.markettrader import MarketTrader
from traders.average.averagetrader import AverageTrader

def handle_cancel(sig, frame):
    print('Cancelled')
    sys.exit(0)

if __name__ == "__main__":
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