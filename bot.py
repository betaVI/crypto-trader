import sys
import signal
import time
from traders.market.markettrader import MarketTrader

def handle_cancel(sig, frame):
    print('Cancelled')
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_cancel)
    runinterval = 5
    productid = 'BTC-USD'
    cash_account_id = 'xxxxxxxxxxxxxxxxxxxxxxxxx'
    crypto_account_id = 'xxxxxxxxxxxxxxxxxxxxxxx'

    trader = MarketTrader(productid, cash_account_id, crypto_account_id)
    while True:
        trader.attemptToMakeMarketTrade()
        # trader.attemptToMkakeLimitTrade()
        print('Waiting ' + str(runinterval) + ' seconds')
        time.sleep(runinterval)