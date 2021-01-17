import sqlite3
from sqlite3 import Error

class DataAccess():
    def __init__(self, path):
        self.path = path +'/Data/trading.db'
        print(self.path)
        self._initializeTables()

    def fetchTraders(self):
        query = "SELECT * FROM traders"
        return self._executeRead(query)
    
    def insertTrader(self, product, baseaccount, qouteaccount, buyupperthreshold, buylowerthreshold, sellupperthreshold, selllowerthreshold):
        values = (product, baseaccount, qouteaccount, buyupperthreshold, buylowerthreshold, sellupperthreshold, selllowerthreshold)
        inserttrader = """INSERT INTO traders (product, baseaccount, qouteaccount, buyupperthreshold, buylowerthreshold, sellupperthreshold, selllowerthreshold)
                            VALUES (?,?,?,?,?,?,?)"""
        self._execute(inserttrader,values)

    def _create_connection(self):
        connection = None
        try:
            connection = sqlite3.connect(self.path)
            print('Connection to SQLite DB successful')
        except Error as e:
            print(f"The error '{e}' occurred")
        return connection

    def _initializeTables(self):
        create_traders_table = """CREATE TABLE IF NOT EXISTS traders(
                                        id integer PRIMARY KEY,
                                        product text NOT NULL,
                                        baseaccount NOT NULL,
                                        qouteaccount NOT NULL,
                                        lastpurcahseprice REAL NULL,
                                        buyupperthreshold REAL NOT NULL,
                                        buylowerthreshold REAL NOT NULL,
                                        sellupperthreshold REAL NOT NULL,
                                        selllowerthreshold REAL NOT NULL
                                    )"""
        self._execute(create_traders_table)

    def _execute(self, statement, params=None):
        with self._create_connection() as conn:
            c = conn.cursor()
            try:
                if params == None:
                    c.execute(statement)
                else:
                    c.execute(statement, params)
            except Error as e:
                print(f"Sql Error: '{e}'")
            finally:
                c.close()

    def _executeRead(self,statement):
        with self._create_connection() as conn:
            c = conn.cursor()
            try:
                c.execute(statement)
                result = c.fetchall()
                return result
            except Error as e:
                print(f"Sql Read Error: '{e}'")
            finally:
                c.close()