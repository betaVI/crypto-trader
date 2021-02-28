from configLoader import loadConfig
from psycopg2.extras import RealDictCursor
import psycopg2

class DataAccess():
    def __init__(self):
        self._initializeTables()

    def execute(self, statement, params=None):
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

    def executeRead(self,statement, values=None):
        with self._create_connection() as conn:
            c = conn.cursor(cursor_factory=RealDictCursor)
            try:
                c.execute(statement, values)
                result = c.fetchall()
                return result
            except (Exception, psycopg2.DatabaseError) as e:
                print(f"Sql Read Error: '{e}'")
            finally:
                c.close()
    
    def executeScalar(self,statement, values=None):
        with self._create_connection() as conn:
            c = conn.cursor(cursor_factory=RealDictCursor)
            try:
                c.execute(statement,values)
                result = c.fetchone()
                return result
            except (Exception, psycopg2.DatabaseError) as e:
                print(f"Sql Read Error: '{e}'")
            finally:
                c.close()

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
                                    id BIGSERIAL PRIMARY KEY,
                                    ordergroupid BIGINT NOT NULL REFERENCES ordergroups(id) ON DELETE CASCADE,
                                    side TEXT NOT NULL,
                                    referenceid UUID NOT NULL,
                                    size NUMERIC(16,10) NOT NULL,
                                    funds NUMERIC(16,10) NOT NULL,
                                    price NUMERIC(16,10) NOT NULL,
                                    fee NUMERIC(16,10) NOT NULL,
                                    createdat TIMESTAMP NOT NULL DEFAULT now()
                                )"""
        
        create_ordergroups_table = """CREATE TABLE IF NOT EXISTS ordergroups (
                                        id BIGSERIAL PRIMARY KEY,
                                        productid INT NOT NULL REFERENCES products(id),
                                        totalearned NUMERIC(16,10) NULL,
                                        totalsize NUMERIC(16,10) NULL,
                                        totalfees NUMERIC(16,10) NULL,
                                        updatedat TIMESTAMP NULL,
                                        createdat TIMESTAMP NOT NULL DEFAULT now()
                                    )"""

        create_log_table = """CREATE TABLE IF NOT EXISTS traderlogs (
                                id BIGSERIAL PRIMARY KEY,
                                loggername TEXT NOT NULL,
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

        self.execute(create_exchanges_table)
        self.execute(create_products_table)
        self.execute(create_traders_table)
        self.execute(create_status_table)
        self.execute(create_orders_table)
        self.execute(create_ordergroups_table)
        self.execute(create_log_table)
        self.execute("INSERT INTO exchanges (name) VALUES ('CoinbasePro') ON CONFLICT DO NOTHING")
        self.execute("INSERT INTO status (name) VALUES ('Active'),('Disabled') ON CONFLICT DO NOTHING")