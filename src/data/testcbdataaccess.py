import uuid, logging
from src.data.dataaccess import DataAccess
from src.data.logsrepository import LogsRepository
from src.bots.dbloghandler import DbLogHandler
from dependency_injector.wiring import Provide

class TestCbDataAccess(DataAccess):
    def __init__(self, host, port, database, user, password, logrepo: LogsRepository):
        super().__init__(host, port, database, user, password)
        self.logger = logging.getLogger('TestCBDB')
        self.logger.addHandler(DbLogHandler(logrepo))
        self.logger.setLevel(logging.DEBUG)

    def getAccounts(self):
        self.logger.debug("Test")
        return self.executeRead("SELECT a.accountid as id, a.product as currency, sum(case when side is null then 0 when side = 'sell' then -size else size end) as balance from account a left join productorder po on a.product = po.product group by a.accountid, a.product")

    def getAccountBalance(self, accountid):
        results = self.executeRead("SELECT coalesce(sum(case when side is null then 0 when side = 'sell' then -size else size end), 0) as balance from productorder where accountid = %s",(accountid,))
        return next(iter(results))

    def createAccount(self, accountid, product):
        self.logger.debug("Looking up account for product '{}'".format(product))
        accounts = self.executeRead("select id, accountid from account where product = %s", (product,))
        length = len(accounts)
        if length > 0:
            self.logger.debug("Found {} accounts for product '{}'".format(length, product))
            previousaccounts = [a for a in accounts if a['accountid'] != accountid]
            currentaccount = next(iter([a for a in accounts if a['accountid'] == accountid]), None)

            #create new record 
            if currentaccount is None:
                self.logger.debug("Creating account for accountid '{}' and product '{}'".format(length, accountid, product))
                self.executeScalar("INSERT INTO account (accountid, product) VALUES(%s,%s)",(accountid, product))
            
            #update productorder table with new record id if any old records exist
            #then delete the old account record
            for a in previousaccounts:
                self.execute("UPDATE productorder SET accountid = %s where accountid = %s", (accountid, a['accountid']))
                self.logger.debug("Updated productorder table for accountid '{}' and product '{}'".format(length, accountid, product))
                self.execute("DELETE FROM account WHERE id = %s", (a['id'],))
                self.logger.debug("Deleted account record for accountid '{}' and product '{}'".format(length, accountid, product))
        else:
            self.logger.debug("Creating accountid '{}' for product '{}'".format(accountid, product))
            self.execute("INSERT INTO account (accountid, product) VALUES(%s,%s)",(accountid, product))

    def createOrder(self, side, product, referenceid, size, funds, price, fee):
        if '-USD' in product:
            product = product[:product.find('-USD')]
        # row = self.executeScalar("select accountid from account where product = %s",(product,))
        # values = (side, product, row['accountid'], referenceid, size, funds, price, fee)
        # query = ','.join(['%s']*len(values))
        # query = "INSERT INTO productorder (side, product, accountid, referenceid, size, funds, price, fee) VALUES ({})".format(query)
        values = {
            'product': product,
            'side': side,
            'referenceid': referenceid,
            'size': size,
            'funds': funds,
            'price': price,
            'fee': fee
        }
        query = "CALL create_order(%(product)s, %(side)s, %(referenceid)s, %(size)s, %(funds)s, %(price)s, %(fee)s)"
        self.execute(query,values)

    def _initializeTables(self):
        create_accounts_table = """CREATE TABLE IF NOT EXISTS account (
                                        id BIGSERIAL PRIMARY KEY,
                                        product TEXT NOT NULL,
                                        accountid TEXT NOT NULL,
                                        CONSTRAINT unique_accountid UNIQUE (accountid)
                                    )"""

        create_order_table = """CREATE TABLE IF NOT EXISTS productorder (
                                    id BIGSERIAL PRIMARY KEY,
                                    side TEXT NOT NULL,
                                    product TEXT NOT NULL,
                                    accountid TEXT NOT NULL,
                                    referenceid UUID NOT NULL,
                                    size NUMERIC(16,10) NOT NULL,
                                    funds NUMERIC(16,10) NOT NULL,
                                    price NUMERIC(16,10) NOT NULL,
                                    fee NUMERIC(16,10) NOT NULL,
                                    createdat TIMESTAMP NOT NULL DEFAULT now()
                                )"""
        
        create_create_order_sproc = """CREATE OR REPLACE PROCEDURE create_order(_product TEXT, _side TEXT, _referenceid UUID, _size NUMERIC(16,10), _funds NUMERIC(16,10), _price NUMERIC(16,10), _fee NUMERIC(16,10))
                                        LANGUAGE plpgsql
                                        AS $$
                                        DECLARE
                                            _accountid TEXT;
                                        BEGIN
                                            SELECT accountid FROM account WHERE product = _product INTO _accountid;

                                            INSERT INTO productorder 
                                                (side, product, accountid, referenceid, size, funds, price, fee) 
                                            VALUES 
                                                (_side, _product, _accountid, _referenceid, _size, _funds, _price, _fee);

                                        END $$;
                                    """
        
        self.execute(create_accounts_table)
        self.execute(create_order_table)
        self.execute(create_create_order_sproc)

    def initializeUSDBankAccount(self):
        row = self.executeScalar("select accountid from account where product = 'USD'")
        account = self.getAccountBalance(row['accountid'])
        if int(account['balance']) < 300:
            self.createOrder('buy', 'USD', str(uuid.uuid4()), 300, 0, 0, 0)

    def updateAccountTableConstraint(self):
        row = self.executeScalar("select count(*) as cnt from information_schema.constraint_column_usage where constraint_name = 'unique_product_account'")
        if int(row['cnt']) == 0:
            self.execute("ALTER TABLE account ADD CONSTRAINT unique_product_account UNIQUE(product)")