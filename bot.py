import sys
import signal
import time
from trader import Trader

def handle_cancel(sig, frame):
    print('Cancelled')
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_cancel)
    runinterval = 10
    trader = Trader()
    while True:
        trader.attemptToMakeTrade()
        print('Waiting ' + str(runinterval) + ' seconds')
        time.sleep(runinterval)