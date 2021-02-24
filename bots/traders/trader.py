import logging
from dbloghandler import DbLogHandler
from bots.cpapi import CbApi
from bots.datamanager import DataManager

class Trader:
    def __init__(self, productid, cashaccount, cryptoaccount, dataaccess):
        self.cash_account_id = cashaccount
        self.crypto_account_id = cryptoaccount
        self.product_id = productid

        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console.setFormatter(logging.Formatter(fmt='%(asctime)s - %(message)s', datefmt='%m-%d-%Y %H:%M:%S'))

        dbhandler = DbLogHandler()
        dbhandler.setLevel(logging.DEBUG)

        logging.getLogger(self.product_id).addHandler(dbhandler)
        logging.info("Start")
        
        self.api = CbApi()