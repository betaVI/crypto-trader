import os, sys, time, signal, json, logging, uuid, random
from bots.cpapi import CbApi
from bots.libs.websocket_client import WebsocketClient
from bots.traders.testtrader import TestTrader
from data.dataaccess import DataAccess
from data.traderrepository import TraderRepository
from data.logsrepository import LogsRepository
from data.ordersrepository import OrdersRepository
from dbloghandler import DbLogHandler

api = CbApi()
db = DataAccess()
logrepo = LogsRepository(db)
traderrepo = TraderRepository(db)
orderrepo = OrdersRepository(db)
loghandler = DbLogHandler(logrepo)

console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
console.setFormatter(logging.Formatter(fmt='%(asctime)s | %(levelname)-8s | %(name)-8s | %(message)s', datefmt='%m-%d-%Y %H:%M:%S'))
logging.getLogger('').addHandler(loghandler)
logging.getLogger('').addHandler(console)

class TestApi():
    def __init__(self, api, dataaccess):
        self.api = api
        self.dataaccess = dataaccess

    def getMarketPrice(self, productid):
        return self.api.getMarketPrice(productid)

    def getRecentTrades(self, product, side, count):
        return self.api.getRecentTrades(product, side, count)

    def getAccountDetails(self, accountid):
        return self.api.getAccountDetails(accountid)
    
    def getFees(self):
        return self.api.getFees()

    def placeMarketOrder(self, product_id, side, funds = None, size = None):
        orderid = str(uuid.uuid4())
        price = self.api.getMarketPrice(product_id)
        feepercent = self.getFees()
        if side == 'buy':
            fee = funds*feepercent
            size = (funds-fee)/price
            usd_volume = funds
        else:
            query = """select sum(o.size) as totalsize
                        from ordergroups og
                        inner join products p on p.id = og.productid
                        inner join orders o on o.ordergroupid = og.id
                        where p.name = %s
                        and og.updatedat is null"""
            size = float(self.dataaccess.executeScalar(query,(product_id,))['totalsize'])

            usd_volume = size*price
            fee = usd_volume*feepercent
            usd_volume -= fee

        return orderid, price, usd_volume, size, fee
        

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
    return traderrepo.getActiveTraders()
    # dicttraders = {t['product']:t for t in traders}
    # return dicttraders

def handle_cancel(sig, frame):
    print('Cancelled')
    sys.exit(0)

if __name__ == "__main__":
    testapi = TestApi(api, db)
    print('cwd is %s' %(os.getcwd()))
    signal.signal(signal.SIGINT, handle_cancel)
    runinterval = 5

    while True:
        activeTraders = getActiveTraders(traderrepo)
        for traderconfig in activeTraders:
            trader = TestTrader(orderrepo, traderconfig, testapi)
            trader.attemptToMakeTrade()
        print('Waiting ' + str(runinterval) + ' seconds')
        time.sleep(runinterval)