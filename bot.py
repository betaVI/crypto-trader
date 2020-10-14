import sys
import signal
import time
from market.markettrader import MarketTrader

def handle_cancel(sig, frame):
    print('Cancelled')
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_cancel)
    runinterval = 5
    trader = MarketTrader()
    while True:
        trader.attemptToMakeMarketTrade()
        # trader.attemptToMkakeLimitTrade()
        print('Waiting ' + str(runinterval) + ' seconds')
        time.sleep(runinterval)