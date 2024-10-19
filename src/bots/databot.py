import os, sys, time, signal, logging, threading
from dependency_injector.wiring import Provide, inject
from src.bots.dbloghandler import DbLogHandler
from src.container import Container, create_container
from src.services.cpapi import CbApi
from src.bots.traders.testtrader import TestTrader
from src.data.dataaccess import DataAccess
from src.data.traderrepository import TraderRepository
from src.data.logsrepository import LogsRepository
from src.data.ordersrepository import OrdersRepository

truncate_logs_timer : threading.Timer = None

def handle_cancel(sig, frame):
    botlogger = logging.getLogger('BOT')
    botlogger.debug('Cancelled')
    if truncate_logs_timer:
        truncate_logs_timer.cancel()
        botlogger.debug('Timer Cancelled')
    sys.exit(0)

def truncate_logs(logrepo: LogsRepository, log_interval: int, log_frequency: str):
    utillogger = logging.getLogger('UTIL')
    utillogger.setLevel(logging.DEBUG)
    utillogger.debug('Removing Logs older than {} {}'.format(log_interval, log_frequency))
    logrepo.purgeLogs(log_interval, log_frequency)
    utillogger.debug('Removed Logs older than {} {}'.format(log_interval, log_frequency))

def runbots(db: DataAccess, api: CbApi, traderrepo: TraderRepository, orderrepo: OrdersRepository):
    while True:
        settings = db.executeScalar("SELECT * FROM settings")
        runinterval = int(settings['interval'])
        loglevel = int(settings['loglevel'])
        botlogger = logging.getLogger('BOT')
        botlogger.setLevel(loglevel)

        products =[p for p in api.getProducts() if p['id'].endswith('USD')]
        for product in products:
            traderrepo.updateProduct(1, product['id'], 0)

        activeTraders = traderrepo.getActiveTraders()
        for traderconfig in activeTraders:
            trader = TestTrader(orderrepo, traderconfig, api)
            if trader.attemptToMakeTrade() and trader.cashout:
                traderrepo.deleteTrader(int(traderconfig['id']))
        
        botlogger.debug('Waiting ' + str(runinterval) + ' seconds')

        time.sleep(runinterval)

@inject
def runapp(
    api: CbApi = Provide[Container.cbapi_client],
    db: DataAccess = Provide[Container.db],
    logrepo: LogsRepository = Provide[Container.logs_repo],
    traderrepo: TraderRepository = Provide[Container.traders_repo],
    orderrepo: OrdersRepository = Provide[Container.orders_repo],
    log_interval: int = Provide[Container.config.logretention.interval.as_(int)],
    log_frequency: str = Provide[Container.config.logretention.frequency]
    ):

    loghandler = DbLogHandler(logrepo)
    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter(fmt='%(asctime)s | %(levelname)-8s | %(name)-8s | %(message)s', datefmt='%m-%d-%Y %H:%M:%S'))
    logging.getLogger('').addHandler(loghandler)
    logging.getLogger('').addHandler(console)

    signal.signal(signal.SIGINT, handle_cancel)

    #start truncate_logs timer process to remove old logs
    truncate_logs_timer = threading.Timer(interval=30.0, function=truncate_logs, args=(logrepo, log_interval, log_frequency))
    truncate_logs_timer.start()

    #start main process
    runbots(db,api, traderrepo, orderrepo)

    #log when process has ended
    botlogger = logging.getLogger('BOT')
    botlogger.debug('Completed')

if __name__ == "__main__":
    create_container(__name__)
    runapp()