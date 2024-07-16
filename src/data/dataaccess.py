from psycopg2.extras import RealDictCursor
import psycopg2, logging, traceback

class DataAccess():
    def __init__(self, host, port, dbname, user, password):
        self._connectionparameters = {
            "dbname": dbname,
            "user": user,
            "password": password,
            "host": host,
        }
        if port != 0:
            self._connectionparameters["port"] = port

        self.logger = logging.getLogger('DataAccess')
        self.logger.setLevel(logging.DEBUG)
        self._initializeTables()

    def createFilter(self,filters):
        conditions = [' {} {} %s'.format(filter['name'],filter['operator']) for filter in filters]
        where =' AND '.join(conditions)
        if len(where) > 0:
            where = 'WHERE ' + where
        return where, tuple([f['value'] for f in filters])

    def execute(self, statement, params=None):
        with self._create_connection() as conn:
            c = conn.cursor()
            try:
                if params == None:
                    c.execute(statement)
                else:
                    c.execute(statement, params)
            except (Exception, psycopg2.DatabaseError) as e:
                self.logger.error('Exception in execute: {} | {}: {}'.format(statement,params, traceback.format_exc()))
            finally:
                c.close()

    def executeRead(self,statement, values=None):
        with self._create_connection() as conn:
            c = conn.cursor(cursor_factory=RealDictCursor)
            try:
                c.execute(statement, values)
                result = c.fetchall()
                return result
            except (Exception, psycopg2.DatabaseError) as e:
                self.logger.error('Exception in executeRead: {} | {}: {}'.format(statement,values, traceback.format_exc()))
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
                self.logger.error('Exception in executeScalar: {} | {}: {}'.format(statement,values, traceback.format_exc()))
            finally:
                c.close()

    def _create_connection(self):
        connection = None
        try:
            connection = psycopg2.connect(**self._connectionparameters)
        except (Exception, psycopg2.DatabaseError) as e:
            self.logger.error('Exception in _create_connection: {}'.format(traceback.format_exc()))
        return connection

    def _initializeTables(self):
        create_products_table = """CREATE TABLE IF NOT EXISTS products (
                                        id SERIAL PRIMARY KEY,
                                        exchangeid smallint NOT NULL references exchanges(id),
                                        name text NOT NULL,
                                        currentprice numeric(16,10) NOT NULL,
                                        createdat timestamp NOT NULL DEFAULT now(),
                                        updatedat timestamp NOT NULL DEFAULT now(),
                                        CONSTRAINT unique_product_name_ix UNIQUE (exchangeid,name)
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
                                        statusid smallint NOT NULL references status(id),
                                        loglevel smallint NOT NULL
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
                                        saleprice NUMERIC(16,10) NULL,
                                        totalearned NUMERIC(16,10) NULL,
                                        totalsize NUMERIC(16,10) NULL,
                                        totalfees NUMERIC(16,10) NULL,
                                        totalspent NUMERIC(16,10) NULL,
                                        updatedat TIMESTAMP NULL,
                                        createdat TIMESTAMP NOT NULL DEFAULT now()
                                    )"""

        create_log_table = """CREATE TABLE IF NOT EXISTS traderlogs (
                                id BIGSERIAL PRIMARY KEY,
                                loggername TEXT NOT NULL,
                                loglevel INT NULL,
                                loglevelname TEXT NULL,
                                filename TEXT NULL,
                                lineno INT NULL,
                                message TEXT NOT NULL,
                                createdat TIMESTAMP NOT NULL DEFAULT now()
                            )"""
                                    
        create_status_table = """CREATE TABLE IF NOT EXISTS status(
                                    id serial PRIMARY KEY,
                                    name text NOT NULL UNIQUE
                                )"""

        create_settings_table = """CREATE TABLE IF NOT EXISTS settings(
                                        interval INT NOT NULL DEFAULT 60,
                                        loglevel INT NOT NULL DEFAULT 10
                                    )"""

        create_delete_logs_sproc = """CREATE OR REPLACE PROCEDURE delete_logs(days INT, frequency TEXT)
                                        LANGUAGE plpgsql
                                        AS $$
                                        DECLARE
                                            log_date TIMESTAMP := now() - CAST(days || ' ' || frequency as interval);
                                        BEGIN
                                            DELETE from traderlogs where createdat < log_date;
                                        END $$;
                                    """
        
        create_product_insert_sproc = """CREATE OR REPLACE FUNCTION upsert_product(_exchangeid INT, _product TEXT, _currentprice NUMERIC(16,10))
                                            RETURNS INT
                                            LANGUAGE plpgsql
                                            AS $$
                                            DECLARE
                                                _productid INT;
                                            BEGIN
                                                SELECT id FROM products WHERE exchangeid = _exchangeid and name = _product INTO _productid;
                                                IF not found then
                                                    INSERT INTO products
                                                        (exchangeid, name, currentprice)
                                                    VALUES
                                                        (_exchangeid, _product, _currentprice)
                                                    RETURNING id
                                                    INTO _productid;
                                                end if;
                                                RETURN _productid;
                                            END $$;
                                        """
        
        self.execute(create_status_table)
        self.execute(create_exchanges_table)
        self.execute(create_products_table)
        self.execute(create_traders_table)
        self.execute(create_settings_table)
        self.execute(create_ordergroups_table)
        self.execute(create_orders_table)
        self.execute(create_log_table)
        self.execute(create_delete_logs_sproc)
        self.execute(create_product_insert_sproc)
        #create index if not exists log_date_ix on traderlogs (createdat);
        self.execute("INSERT INTO exchanges (name) VALUES ('CoinbasePro') ON CONFLICT DO NOTHING")
        self.execute("INSERT INTO status (name) VALUES ('Active'),('Disabled'),('Cash Out') ON CONFLICT DO NOTHING")
        record = self.executeScalar("SELECT count(*) FROM settings")
        if int(record['count']) == 0:
            self.execute("INSERT INTO settings (interval,loglevel) VALUES (60,10)")