from src.data.dataaccess import DataAccess

class TestCbDataAccess(DataAccess):
    def __init__(self, host, port, database, user, password):
        super().__init__(host, port, database, user, password)

    def getAccounts(self):
        return self.executeRead("SELECT a.accountid as id, a.product as currency, sum(case when side is null then 0 when side = 'sell' then -size else size end) as balance from account a left join productorder po on a.product = po.product group by a.accountid, a.product")

    def getAccountBalance(self, accountid):
        results = self.executeRead("SELECT sum(case when side is null then 0 when side = 'sell' then -size else size end) as balance from productorder where accountid = %s",(accountid,))
        return next(iter(results))

    def createAccount(self, accountid, product):
        self.execute("INSERT INTO account (accountid, product) VALUES(%s,%s) ON CONFLICT DO NOTHING",(accountid, product))

    def createOrder(self, side, product, referenceid, size, funds, price, fee):
        if '-USD' in product:
            product = product[:product.find('-USD')]
        row = self.executeScalar("select accountid from account where product = %s",(product,))
        values = (side, product, row['accountid'], referenceid, size, funds, price, fee)
        query = ','.join(['%s']*len(values))
        query = "INSERT INTO productorder (side, product, accountid, referenceid, size, funds, price, fee) VALUES ({})".format(query)
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
        
        self.execute(create_accounts_table)
        self.execute(create_order_table)