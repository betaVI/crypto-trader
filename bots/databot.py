from bots.cpapi import CbApi
from bots.libs.websocket_client import WebsocketClient
import sys
import time
import json

api = CbApi()

class TradersWebSocket(WebsocketClient):
    def __init__(self, products):
        super().__init__(channels=None)
        self.products = products

    def on_open(self):
        print('Websocket opened')
        pass

    def on_message(self, msg):
        print(json.dumps(msg, indent=4, sort_keys=True))
        pass

    def on_close(self):
        print("Websocket closed")

if __name__ == "__main__":
    products = [p['id'] for p in api.getProducts() if p['id'].endswith('USD')]
    wsclient = TradersWebSocket(products)
    wsclient.start()
    # print(wsclient.url, wsclient.products)
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        wsclient.close()
    sys.exit(0)