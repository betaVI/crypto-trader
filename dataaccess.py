from configLoader import loadConfig
from psycopg2.extras import RealDictCursor
import psycopg2

class DataAccess():
    def __init__(self):
        self._initializeTables()

    def fetchConfiguredProducts(self):
        query = "SELECT p.name as product FROM traders t INNER JOIN status s on s.id = t.statusid INNER JOIN products p on p.id = t.productid"
        return self._executeRead(query)

    def fetchTraders(self):
        query = "SELECT t.*, p.name as product, s.name as statusname FROM traders t INNER JOIN status s on s.id = t.statusid INNER JOIN products p on p.id = t.productid ORDER BY p.name"
        return self._executeRead(query)
    
    def fetchProductTraders(self):
        query = """select 0 as price, p.name as product, s.name as statusname, t.*
                    from products p
                    left join traders t on t.productid = p.id
                    left join status s on s.id = t.statusid
                    order by p.name"""
        return self._executeRead(query)

    def fetchTrader(self, id):
        query = """SELECT 
                        t.id as traderid, p.name as product, baseaccount, quoteaccount, buyupperthreshold, buylowerthreshold, sellupperthreshold, selllowerthreshold, maxpurchaseamount, statusid as status 
                    FROM 
                        traders t inner join 
                        products p on p.id = t.productid 
                    WHERE 
                        t.id = {}""".format(id)
        return next(iter(self._executeRead(query)), None)

    def fetchStatuses(self):
        query = "SELECT * FROM status"
        return self._executeRead(query)
    
    def updateTraderStatus(self, id, status):
        values = (status, id)
        query = "UPDATE traders SET statusid = (SELECT id FROM status WHERE name = %s) WHERE id = %s"
        return self._execute(query, values)

    def alterTrader(self, id, product, baseaccount, quoteaccount, buyupperthreshold, buylowerthreshold, sellupperthreshold, selllowerthreshold, maxpurchaseamount):
        productid = self.updateProduct(1, product, 0)
        values = (productid, baseaccount, quoteaccount, float(buyupperthreshold), float(buylowerthreshold), float(sellupperthreshold), float(selllowerthreshold), float(maxpurchaseamount))
        if id != '0':
            query = """UPDATE traders 
                            SET productid = %s, baseaccount=%s, quoteaccount=%s, buyupperthreshold=%s, buylowerthreshold=%s, sellupperthreshold=%s, selllowerthreshold=%s, maxpurchaseamount=%s
                            WHERE id = {}""".format(id)
        else:
            query = ",".join(['%s']*len(values))
            query = """INSERT INTO traders (productid, baseaccount, quoteaccount, buyupperthreshold, buylowerthreshold, sellupperthreshold, selllowerthreshold, maxpurchaseamount) 
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

    def createLog(self, loggername, loglevel, filename, lineno, message):
        query = "INSERT INTO traderlogs (loggername, loglevel, filename, lineno, message) VALUES ('{}',{},'{}',{},'{}')".format(loggername, loglevel, filename, lineno, message)
        self._execute(query)

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

        create_orders_table = """CREATE TABLE IF NOT EXISTS orders (
                                    id SERIAL PRIMARY KEY,
                                    productid INT NOT NULL REFERENCES products(id),
                                    side TEXT NOT NULL,
                                    referenceid UUID NOT NULL,
                                    size NUMERIC(16,10) NOT NULL,
                                    price NUMERIC(16,10) NOT NULL,
                                    fee NUMERIC(16,10) NOT NULL,
                                    createdat TIMESTAMP NOT NULL DEFAULT now()
                                )"""

        create_log_table = """CREATE TABLE IF NOT EXISTS traderlogs (
                                id SERIAL PRIMARY KEY,
                                loggername INT NOT NULL,
                                loglevel INT NULL,
                                filename TEXT NULL,
                                lineno INT NULL,
                                message TEXT NOT NULL,
                                createdat TIMESTAMP NOT NULL DEFAULT now()
                            )"""
                                    
        create_status_table = """CREATE TABLE IF NOT EXISTS status(
                                    id serial PRIMARY KEY,
                                    name text NOT NULL UNIQUE
                                )"""

        self._execute(create_exchanges_table)
        self._execute(create_products_table)
        self._execute(create_traders_table)
        self._execute(create_status_table)
        self._execute(create_orders_table)
        self._execute(create_log_table)
        self._execute("INSERT INTO exchanges (name) VALUES ('CoinbasePro') ON CONFLICT DO NOTHING")
        self._execute("INSERT INTO status (name) VALUES ('Active'),('Disabled') ON CONFLICT DO NOTHING")

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