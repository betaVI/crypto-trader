import os, sys, time, signal, json, logging
from bots.cpapi import CbApi
from bots.libs.websocket_client import WebsocketClient
from data.dataaccess import DataAccess
from data.traderrepository import TraderRepository
from data.logsrepository import LogsRepository
from traders.testtrader import TestTrader
from dbloghandler import DbLogHandler

api = CbApi()
db = DataAccess()
logrepo = LogsRepository(db)
traderrepo = TraderRepository(db)
loghandler = DbLogHandler(logrepo)
logging.getLogger('').addHandler(loghandler)

# class TradersWebSocket(WebsocketClient):
#     def __init__(self, products):
#         super().__init__(channels=None)
#         self.products = products
#         self.traders = []

#     def on_open(self):
#         print('Websocket opened')

#     def on_message(self, msg):
#         print(json.dumps(msg, indent=4, sort_keys=True))
#         if msg['type'] != "ticker":
#             return

#         if msg['product_id'] in self.traders:
#             trader = self.traders[msg['product_id']]
#             log = logging.getLogger(trader['product'])
#             log.setLevel(logging.DEBUG)
#             log.debug('debug')
#             log.info('info')
#             log.warning('warning')
#             log.error('error')
#             log.critical('critical')

#     def on_close(self):
#         print("Websocket closed")

#     def setTraders(self, traders):
#         self.traders = traders

def getActiveTraders(traderrepo):
    traders = traderrepo.getActiveTraders()
    dicttraders = {t['product']:t for t in traders}
    return dicttraders

def handle_cancel(sig, frame):
    print('Cancelled')
    sys.exit(0)

if __name__ == "__main__":
    print('cwd is %s' %(os.getcwd()))
    signal.signal(signal.SIGINT, handle_cancel)
    runinterval = 5

    while True:
        activeTraders = getActiveTraders(traderrepo)
        for traderconfig in activeTraders:
            trader = TestTrader(traderconfig, api, dbloghandler)
            trader.attemptToMakeTrade()
        print('Waiting ' + str(runinterval) + ' seconds')
        time.sleep(runinterval)