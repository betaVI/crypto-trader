import uuid, logging
from src.data.testcbdataaccess import TestCbDataAccess
from src.services.cpapi import CbApi
from src.services.livecbapi import LiveCbApi

class TestCbApi(LiveCbApi):
    def __init__(self, api_key, api_secret, db: TestCbDataAccess):
        super().__init__(api_key, api_secret)
        self.dataaccess = db
        self.testlogger = logging.getLogger('TEST API')
        self.testlogger.setLevel(logging.DEBUG)
        response = self.client.get_accounts()
        self._loadAccounts(response['accounts'])

    def getAccounts(self):
        return self.dataaccess.getAccounts()

    def getAccountDetails(self, accountid):
        return self.dataaccess.getAccountBalance(accountid)

    def placeMarketOrder(self, product_id, side, funds = None, size = None):
        self.testlogger.debug('[ATTEMPT] {} {} Order for ${} or {}'.format(product_id, side, funds, size))
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
        self.testlogger.debug('[RESULT] {} {} Order: {} = (${}/{}) - {}'.format(product_id, side, usd_volume, price, size, fee))

        self.dataaccess.createOrder('buy' if side == 'sell' else 'sell', 'USD', orderid, usd_volume, 0, 0, 0)
        self.testlogger.debug('[WITHDRAWL] {} {} Order: {} = (${}/{}) - {}'.format('USD', 'buy' if side == 'sell' else 'sell', usd_volume, 0, 0, 0))

        return orderid, price, usd_volume, size, fee

    def _loadAccounts(self, accounts):
        for a in accounts:
            self.dataaccess.createAccount(a['uuid'],a['currency'])
        self.dataaccess.updateAccountTableConstraint()
        
        self.dataaccess.initializeUSDBankAccount()
