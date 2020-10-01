import sys
import signal
import time
from libs.authenticated_client import AuthenticatedClient

def handle_cancel(sig, frame):
    print('Cancelled')
    sys.exit(0)

signal.signal(signal.SIGINT, handle_cancel)

#configuration values
runinterval = 30
key = 'xxxxxxxxxxxxxxxxx'
b64secret = 'xxxxxxxxxxxxxxxxxxxxxx=='
passphrase = 'xxxxxxxxxxxx'
url = 'https://api-public.sandbox.pro.coinbase.com'
#product_id = 'LTC-USD'
product_id = 'BTC-USD'

authClient = AuthenticatedClient(key, b64secret, passphrase, api_url=url)

while True:
    print('Start')

    results = authClient.get_product_ticker(product_id=product_id)
    print(results)

    results = authClient.get_accounts()
    print(results)

    print('End')
    print('Waiting ' + str(runinterval) + ' seconds')
    time.sleep(runinterval)