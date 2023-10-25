import uuid, logging
from src.data.testcbdataaccess import TestCbDataAccess
from src.services.cpapi import CbApi

class TestCbApi(CbApi):
    def __init__(self, key, secret, passphrase, url, db: TestCbDataAccess):
        super().__init__(key, secret, passphrase, url)
        self.dataaccess = db
        self.logger = logging.getLogger('TEST API')
        self.logger.setLevel(logging.DEBUG)
        self._loadAccounts(self.client.get_accounts())

    def getAccounts(self):
        return self.dataaccess.getAccounts()

    def getAccountDetails(self, accountid):
        return self.dataaccess.getAccountBalance(accountid)

    def placeMarketOrder(self, product_id, side, funds = None, size = None):
        self.logger.debug('[ATTEMPT] {} {} Order for ${} or {}'.format(product_id, side, funds, size))
        orderid = str(uuid.uuid4())
        price = self.getMarketPrice(product_id)
        feepercent = self.getFees()
        if side == 'buy':
            fee = funds*feepercent
            size = (funds-fee)/price
            usd_volume = funds
        else:
            usd_volume = size*price
            fee = usd_volume*feepercent
            usd_volume -= fee

        self.dataaccess.createOrder(side,product_id,orderid,size,usd_volume,price,fee)
        self.logger.debug('[RESULT] {} {} Order: {} = (${}/{}) - {}'.format(product_id, side, usd_volume, price, size, fee))

        self.dataaccess.createOrder('buy' if side == 'sell' else 'sell', 'USD', orderid, usd_volume, 0, 0, 0)
        self.logger.debug('[WITHDRAWL] {} {} Order: {} = (${}/{}) - {}'.format('USD', 'buy' if side == 'sell' else 'sell', usd_volume, 0, 0, 0))

        return orderid, price, usd_volume, size, fee

    def _loadAccounts(self, accounts):
        for a in accounts:
            self.dataaccess.createAccount(a['id'],a['currency'])
        
        self.dataaccess.initializeUSDBankAccount()
