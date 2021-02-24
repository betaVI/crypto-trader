class TraderRepository:
    def __init__(self, dataaccess):
        self.dataaccess = dataaccess

    def getActiveTraders(self):
        query = """SELECT p.name as product, baseaccount, quoteaccount, buyupperthreshold, buylowerthreshold, sellupperthreshold, selllowerthreshold, maxpurchaseamount
                    FROM traders t 
                    INNER JOIN products p on p.id = t.productid
                    INNER JOIN status s on s.id = t.statusid
                    WHERE s.name = 'Active'"""
        return self.dataaccess.executeRead(query)

    def fetchConfiguredProducts(self):
        query = "SELECT p.name as product FROM traders t INNER JOIN status s on s.id = t.statusid INNER JOIN products p on p.id = t.productid"
        return self.dataaccess.executeRead(query)

    def fetchProductTraders(self):
        query = """select 0 as price, p.name as product, s.name as statusname, t.*
                    from products p
                    left join traders t on t.productid = p.id
                    left join status s on s.id = t.statusid
                    order by p.name"""
        return self.dataaccess.executeRead(query)

    def fetchTrader(self, id):
        query = """SELECT 
                        t.id as traderid, p.name as product, baseaccount, quoteaccount, buyupperthreshold, buylowerthreshold, sellupperthreshold, selllowerthreshold, maxpurchaseamount, statusid as status 
                    FROM 
                        traders t inner join 
                        products p on p.id = t.productid 
                    WHERE 
                        t.id = {}""".format(id)
        return next(iter(self.dataaccess.executeRead(query)), None)

    def updateTraderStatus(self, id, status):
        values = (status, id)
        query = "UPDATE traders SET statusid = (SELECT id FROM status WHERE name = %s) WHERE id = %s"
        return self.dataaccess.execute(query, values)

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
        
        return self.dataaccess.execute(query,values)

    def deleteTrader(self, id):
        query = "DELETE FROM traders WHERE id = {}".format(id)
        return self.dataaccess.execute(query)

    def updateProduct(self, exchangeid, product, currentprice):

        update_product_query = "INSERT INTO products (exchangeid, name, currentprice) VALUES ({},'{}',{}) ".format(exchangeid,product, currentprice)
        update_product_query += "ON CONFLICT (name) DO UPDATE SET currentprice = {}, updatedat = CURRENT_TIMESTAMP".format(currentprice)

        self.dataaccess.execute(update_product_query)

        row = self.dataaccess.executeRead("SELECT ID FROM products WHERE name = '{}'".format(product))
        return row[0]['id']