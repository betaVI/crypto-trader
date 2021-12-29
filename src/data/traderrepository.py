class TraderRepository:
    def __init__(self, dataaccess):
        self.dataaccess = dataaccess

    def getActiveTraders(self):
        query = """SELECT p.name as product, s.name as status, t.id, loglevel, baseaccount, quoteaccount, buyupperthreshold, buylowerthreshold, sellupperthreshold, selllowerthreshold, maxpurchaseamount, COALESCE(f.totalspent,0) as totalspent
                    FROM traders t 
                    INNER JOIN products p on p.id = t.productid
                    INNER JOIN status s on s.id = t.statusid
                    LEFT JOIN (
                        select og.productid, sum(funds) as totalspent 
                        from orders o 
                        inner join ordergroups og on og.id = o.ordergroupid 
                        where og.updatedat is null 
                        and o.side = 'buy'
                        group by og.productid) f on f.productid = p.id
                    WHERE s.name != 'Disabled'"""
        return self.dataaccess.executeRead(query)

    def fetchConfiguredProducts(self):
        query = "SELECT p.name as product FROM traders t INNER JOIN status s on s.id = t.statusid INNER JOIN products p on p.id = t.productid"
        return self.dataaccess.executeRead(query)

    def getTotalAllowedForTraders(self):
        query = "SELECT SUM(maxpurchaseamount) as total FROM traders"
        return float(self.dataaccess.executeScalar(query)['total'])

    def fetchProductTraders(self):
        query = """select 0 as price, p.name as product, s.name as statusname, COALESCE(f.totalspent,0) as totalspent, t.*
                    from products p
                    left join traders t on t.productid = p.id
                    left join status s on s.id = t.statusid
                    LEFT JOIN (
                        select og.productid, sum(funds) as totalspent 
                        from orders o 
                        inner join ordergroups og on og.id = o.ordergroupid 
                        where og.updatedat is null 
                        and o.side = 'buy'
                        group by og.productid) f on f.productid = p.id
                    order by p.name"""
        return self.dataaccess.executeRead(query)

    def fetchTrader(self, id):
        query = """SELECT 
                        t.id as traderid, loglevel, p.name as product, baseaccount, quoteaccount, buyupperthreshold, buylowerthreshold, sellupperthreshold, selllowerthreshold, maxpurchaseamount, statusid as status 
                    FROM 
                        traders t inner join 
                        products p on p.id = t.productid 
                    WHERE 
                        t.id = %s"""
        return self.dataaccess.executeScalar(query,(id,))

    def updateTraderStatus(self, id, status):
        values = (status, id)
        query = "UPDATE traders SET statusid = (SELECT id FROM status WHERE name = %s) WHERE id = %s"
        return self.dataaccess.execute(query, values)

    def alterTrader(self, id, product, loglevel, baseaccount, quoteaccount, buyupperthreshold, buylowerthreshold, sellupperthreshold, selllowerthreshold, maxpurchaseamount):
        productid = self.updateProduct(1, product, 0)
        values = (productid, loglevel, baseaccount, quoteaccount, float(buyupperthreshold), float(buylowerthreshold), float(sellupperthreshold), float(selllowerthreshold), float(maxpurchaseamount))
        if id != '0':
            query = """UPDATE traders 
                            SET productid = %s, loglevel = %s, baseaccount=%s, quoteaccount=%s, buyupperthreshold=%s, buylowerthreshold=%s, sellupperthreshold=%s, selllowerthreshold=%s, maxpurchaseamount=%s
                            WHERE id = {}""".format(id)
        else:
            query = ",".join(['%s']*len(values))
            query = """INSERT INTO traders (productid, loglevel, baseaccount, quoteaccount, buyupperthreshold, buylowerthreshold, sellupperthreshold, selllowerthreshold, maxpurchaseamount) 
                        VALUES ({})""".format(query)
        
        return self.dataaccess.execute(query,values)

    def deleteTrader(self, id):
        query = "DELETE FROM traders WHERE id = %s"
        return self.dataaccess.execute(query,(id,))

    def updateProduct(self, exchangeid, product, currentprice):
        values =(exchangeid,product, currentprice)
        update_product_query = ','.join(['%s']*len(values))
        update_product_query = "INSERT INTO products (exchangeid, name, currentprice) VALUES ({}) ".format(update_product_query)
        update_product_query += "ON CONFLICT (name) DO UPDATE SET currentprice = {}, updatedat = CURRENT_TIMESTAMP".format(currentprice)

        self.dataaccess.execute(update_product_query, values)

        row = self.dataaccess.executeScalar("SELECT ID FROM products WHERE name = '{}'".format(product))
        return row['id']