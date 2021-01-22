import sqlite3
from sqlite3 import Error

class DataAccess():
    def __init__(self, path):
        self.path = path +'/Data/trading.db'
        print(self.path)
        self._initializeTables()

    def fetchTraders(self):
        query = "SELECT t.*, s.name as statusname FROM traders t INNER JOIN status s on s.id = t.statusid"
        return self._executeRead(query)

    def fetchTrader(self, id):
        query = "SELECT product, baseaccount, quoteaccount, buyupperthreshold, buylowerthreshold, sellupperthreshold, selllowerthreshold, statusid as status FROM traders t WHERE t.id = {}".format(id)
        return next(iter(self._executeRead(query)), None)

    def fetchStatuses(self):
        query = "SELECT * FROM status"
        return self._executeRead(query)
    
    def alterTrader(self, id, product, baseaccount, quoteaccount, buyupperthreshold, buylowerthreshold, sellupperthreshold, selllowerthreshold, statusid):
        values = (product, baseaccount, quoteaccount, float(buyupperthreshold), float(buylowerthreshold), float(sellupperthreshold), float(selllowerthreshold), int(statusid))
        if id != 0:
            query = """UPDATE traders 
                            SET product = ?, baseaccount=?, quoteaccount=?, buyupperthreshold=?, buylowerthreshold=?, sellupperthreshold=?, selllowerthreshold=?, statusid=?
                            WHERE id = {}""".format(id)
        else:
            query = """INSERT INTO traders (product, baseaccount, quoteaccount, buyupperthreshold, buylowerthreshold, sellupperthreshold, selllowerthreshold, statusid) 
                        VALUES (?,?,?,?,?,?,?,?)"""
        
        return self._execute(query,values)

    def deleteTrader(self, id):
        query = "DELETE FROM traders WHERE id = {}".format(id)
        return self._execute(query)

    def _create_connection(self):
        connection = None
        try:
            connection = sqlite3.connect(self.path)
            # print('Connection to SQLite DB successful')
        except Error as e:
            print(f"The error '{e}' occurred")
        return connection

    def _initializeTables(self):
        create_traders_table = """CREATE TABLE IF NOT EXISTS traders(
                                        id integer PRIMARY KEY,
                                        product text NOT NULL,
                                        baseaccount text NOT NULL,
                                        quoteaccount text NOT NULL,
                                        lastpurcahseprice REAL NULL,
                                        buyupperthreshold REAL NOT NULL,
                                        buylowerthreshold REAL NOT NULL,
                                        sellupperthreshold REAL NOT NULL,
                                        selllowerthreshold REAL NOT NULL,
                                        statusid integer NOT NULL,
                                        FOREIGN KEY (statusid) REFERENCES status (id)
                                    )"""
                                    
        create_status_table = """CREATE TABLE IF NOT EXISTS status(
                                    id integer PRIMARY KEY,
                                    name text NOT NULL UNIQUE
                                )"""

        self._execute(create_traders_table)
        self._execute(create_status_table)
        self._execute("""INSERT OR IGNORE INTO status (name) VALUES ('Active'),('Disabled')""")

        if self._columnNotExists('traders','statusid'):
            self._updateTable('traders', create_traders_table, """INSERT INTO traders (product, baseaccount, quoteaccount, buyupperthreshold, buylowerthreshold, sellupperthreshold, selllowerthreshold, statusid)
                            SELECT product, baseaccount, quoteaccount, buyupperthreshold, buylowerthreshold, sellupperthreshold, selllowerthreshold, 1 FROM traders_old""")

    def _columnNotExists(self, table, column):
        with self._create_connection() as conn:
            c = conn.cursor()
            try:
                columns = c.execute("PRAGMA table_info(" + table + ")")
                columns = [i[1] for i in columns]
                return column not in columns
            except Error as e:
                print(f"Find Column Error: '{e}'")
            finally:
                c.close()

    def _updateTable(self, tablename, createquery, insertquery):
        oldtablename = tablename + "_old"
        with self._create_connection() as conn:
            c = conn.cursor()
            try:
                c.execute("PRAGMA forign_keys=off")
                c.execute("BEGIN TRANSACTION")
                c.execute("ALTER TABLE " + tablename + " RENAME TO " + oldtablename)
                c.execute(createquery)
                c.execute(insertquery)
                c.execute("DROP TABLE " + oldtablename)
                c.execute("COMMIT")
                c.execute("PRAGMA forign_keys=on")
            except Error as e:
                print(f"Table Update Error: '{e}'")
            finally:
                c.close()

    def _execute(self, statement, params=None):
        error = None
        with self._create_connection() as conn:
            c = conn.cursor()
            try:
                if params == None:
                    c.execute(statement)
                else:
                    c.execute(statement, params)
            except Error as e:
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
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            try:
                c.execute(statement)
                result = c.fetchall()
                return result
            except Error as e:
                print(f"Sql Read Error: '{e}'")
            finally:
                c.close()