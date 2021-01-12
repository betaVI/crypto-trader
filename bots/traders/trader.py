import logging
from bots.cpapi import CbApi
from bots.datamanager import DataManager

class Trader:
    def __init__(self, productid, cashaccount, cryptoaccount, logFileName, dataFileName):
        self.cash_account_id = cashaccount
        self.crypto_account_id = cryptoaccount
        self.product_id = productid

        logging.basicConfig(level=logging.INFO, filename=logFileName, format='%(asctime)s - %(message)s', datefmt='%m-%d-%Y %H:%M:%S')
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console.setFormatter(logging.Formatter(fmt='%(asctime)s - %(message)s', datefmt='%m-%d-%Y %H:%M:%S'))
        logging.getLogger().addHandler(console)
        logging.info("Start")
        
        self.api = CbApi()
        self.dm = DataManager(dataFileName)