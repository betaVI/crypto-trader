import sys
import signal
import time
from libs.public_client import PublicClient

def handle_cancel(sig, frame):
    print('Cancelled')
    sys.exit(0)

signal.signal(signal.SIGINT, handle_cancel)

#configuration values
runinterval = 30
url = 'https://api-public.sandbox.pro.coinbase.com'
#product_id = 'LTC-USD'
product_id = 'BTC-USD'

publicClient = PublicClient(api_url=url)

while True:
    print('Start')

    results = publicClient.get_product_ticker(product_id=product_id)
    print(results)

    print('End')
    print('Waiting ' + str(runinterval) + ' seconds')
    time.sleep(runinterval)