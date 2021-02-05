from configLoader import loadConfig
from psycopg2.extras import RealDictCursor
import psycopg2

class DataAccess():
    def __init__(self):
        self._initializeTables()

    def fetchTraders(self):
        query = "SELECT t.*, p.name as product, s.name as statusname FROM traders t INNER JOIN status s on s.id = t.statusid INNER JOIN products p on p.id = t.productid"
        return self._executeRead(query)

    def fetchTrader(self, id):
        query = """SELECT 
                        p.name as product, baseaccount, quoteaccount, buyupperthreshold, buylowerthreshold, sellupperthreshold, selllowerthreshold, statusid as status 
                    FROM 
                        traders t inner join 
                        products p on p.id = t.productid 
                    WHERE 
                        t.id = {}""".format(id)
        return next(iter(self._executeRead(query)), None)

    def fetchStatuses(self):
        query = "SELECT * FROM status"
        return self._executeRead(query)
    
    def alterTrader(self, id, product, baseaccount, quoteaccount, buyupperthreshold, buylowerthreshold, sellupperthreshold, selllowerthreshold, maxpurchaseamount, statusid):
        productid = self.updateProduct(1, product, 0)
        values = (productid, baseaccount, quoteaccount, float(buyupperthreshold), float(buylowerthreshold), float(sellupperthreshold), float(selllowerthreshold), float(maxpurchaseamount), int(statusid))
        if id != '0':
            query = """UPDATE traders 
                            SET productid = %s, baseaccount=%s, quoteaccount=%s, buyupperthreshold=%s, buylowerthreshold=%s, sellupperthreshold=%s, selllowerthreshold=%s, maxpurchaseamount=%s, statusid=%s
                            WHERE id = {}""".format(id)
        else:
            query = ",".join(['%s']*len(values))
            query = """INSERT INTO traders (productid, baseaccount, quoteaccount, buyupperthreshold, buylowerthreshold, sellupperthreshold, selllowerthreshold, maxpurchaseamount, statusid) 
                        VALUES ({})""".format(query)
        
        return self._execute(query,values)

    def deleteTrader(self, id):
        query = "DELETE FROM traders WHERE id = {}".format(id)
        return self._execute(query)

    def updateProduct(self, exchangeid, product, currentprice):

        update_product_query = "INSERT INTO products (exchangeid, name, currentprice) VALUES ({},'{}',{}) ".format(exchangeid,product, currentprice)
        update_product_query += "ON CONFLICT (name) DO UPDATE SET currentprice = {}, updatedat = CURRENT_TIMESTAMP".format(currentprice)

        self._execute(update_product_query)

        row = self._executeRead("SELECT ID FROM products WHERE name = '{}'".format(product))
        return row[0]['id']

    def _create_connection(self):
        connection = None
        try:
            dbconfig = loadConfig('../database.ini', 'postgresdb')
            connection = psycopg2.connect(**dbconfig)
        except (Exception, psycopg2.DatabaseError) as e:
            print(f"The error '{e}' occurred")
        return connection

    def _initializeTables(self):
        create_products_table = """CREATE TABLE IF NOT EXISTS products (
                                        id SERIAL PRIMARY KEY,
                                        exchangeid smallint NOT NULL references exchanges(id),
                                        name text NOT NULL,
                                        currentprice numeric(16,10) NOT NULL,
                                        createdat timestamp NOT NULL DEFAULT now(),
                                        updatedat timestamp NOT NULL DEFAULT now(),
                                        CONSTRAINT unique_product_name UNIQUE (name)
                                    )"""
        
        create_exchanges_table = """CREATE TABLE IF NOT EXISTS exchanges (
                                        id serial PRIMARY KEY,
                                        name text NOT NULL,
                                        CONSTRAINT unique_exhcange_name UNIQUE (name)
                                    )"""
        
        create_traders_table = """CREATE TABLE IF NOT EXISTS traders(
                                        id SERIAL PRIMARY KEY,
                                        productid int NOT NULL REFERENCES products(id),
                                        baseaccount text NOT NULL,
                                        quoteaccount text NOT NULL,
                                        lastpurchaseprice numeric(16,10) NULL,
                                        maxpurchaseamount numeric(16,10) NOT NULL,
                                        buyupperthreshold Numeric(3,2) NOT NULL,
                                        buylowerthreshold Numeric(3,2) NOT NULL,
                                        sellupperthreshold Numeric(3,2) NOT NULL,
                                        selllowerthreshold Numeric(3,2) NOT NULL,
                                        statusid smallint NOT NULL references status(id)
                                    )"""
                                    
        create_status_table = """CREATE TABLE IF NOT EXISTS status(
                                    id serial PRIMARY KEY,
                                    name text NOT NULL UNIQUE
                                )"""

        self._execute(create_exchanges_table)
        self._execute(create_products_table)
        self._execute(create_traders_table)
        self._execute(create_status_table)
        self._execute("INSERT INTO exchanges (name) VALUES ('CoinbasePro') ON CONFLICT DO NOTHING")
        self._execute("INSERT INTO status (name) VALUES ('Active'),('Disabled') ON CONFLICT DO NOTHING")

    def _checkTableForColumn(self, table, column):
        query = """SELECT EXISTS (
            SELECT 1 FROM information_schema.columns WHERE table_schema='public' AND table_name='{}' AND column_name='{}'
        )""".format(table,column)
        result = self._executeRead(query)
        return result[0]['exists']

    def _checkForConstraint(self, constraintname):
        query = "SELECT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = '{}')".format(constraintname)
        result = self._executeRead(query)
        return result[0]['exists']

    def _execute(self, statement, params=None):
        error = None
        with self._create_connection() as conn:
            c = conn.cursor()
            try:
                if params == None:
                    c.execute(statement)
                else:
                    c.execute(statement, params)
            except (Exception, psycopg2.DatabaseError) as e:
                error = f"Sql Error: '{e}'"
            finally:
                c.close()
        return error

    # def _executeMany(self, statement, sequence):
    #     with self._create_connection() as conn:
    #         c = conn.cursor()
    #         try:
    #             c.executemany(statement, sequence)
    #         except Error as e:
    #             print(f"Sql Error: '{e}'")
    #         finally:
    #             c.close()

    def _executeRead(self,statement):
        with self._create_connection() as conn:
            c = conn.cursor(cursor_factory=RealDictCursor)
            try:
                c.execute(statement)
                result = c.fetchall()
                return result
            except (Exception, psycopg2.DatabaseError) as e:
                print(f"Sql Read Error: '{e}'")
            finally:
                c.close()