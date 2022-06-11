import os, sys, time, signal, logging
from dependency_injector.wiring import Provide, inject
from src.bots.dbloghandler import DbLogHandler
from src.container import Container, create_container
from src.services.cpapi import CbApi
from src.bots.traders.testtrader import TestTrader
from src.data.dataaccess import DataAccess
from src.data.traderrepository import TraderRepository
from src.data.logsrepository import LogsRepository
from src.data.ordersrepository import OrdersRepository

def handle_cancel(sig, frame):
    print('Cancelled')
    sys.exit(0)

@inject
def runapp(
    api: CbApi = Provide[Container.cbapi_client],
    db: DataAccess = Provide[Container.db],
    logrepo: LogsRepository = Provide[Container.logs_repo],
    traderrepo: TraderRepository = Provide[Container.traders_repo],
    orderrepo: OrdersRepository = Provide[Container.orders_repo]
    ):

    loghandler = DbLogHandler(logrepo)
    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter(fmt='%(asctime)s | %(levelname)-8s | %(name)-8s | %(message)s', datefmt='%m-%d-%Y %H:%M:%S'))
    logging.getLogger('').addHandler(loghandler)
    logging.getLogger('').addHandler(console)

    print('cwd is %s' %(os.getcwd()))
    signal.signal(signal.SIGINT, handle_cancel)

    while True:
        settings = db.executeScalar("SELECT * FROM settings")
        runinterval = int(settings['interval'])
        loglevel = int(settings['loglevel'])
        console.setLevel(loglevel)

        products =[p for p in api.getProducts() if p['id'].endswith('USD')]
        for product in products:
            traderrepo.updateProduct(1, product['id'], 0)

        activeTraders = traderrepo.getActiveTraders()
        for traderconfig in activeTraders:
            loghandler.setLevel(int(traderconfig['loglevel']))
            trader = TestTrader(orderrepo, traderconfig, api)
            if trader.attemptToMakeTrade() and trader.cashout:
                traderrepo.deleteTrader(int(traderconfig['id']))
        
        print('Waiting ' + str(runinterval) + ' seconds')
        logrepo.purgeLogs()

        time.sleep(runinterval)

if __name__ == "__main__":
    container = create_container(__name__)
    runapp()