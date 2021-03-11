class OrdersRepository():
    def __init__(self, dataaccess):
        self.dataaccess = dataaccess

    def getOrderProducts(self):
        query = "SELECT distinct p.name from ordergroups og inner join products p on p.id = og.productid"
        return self.dataaccess.executeRead(query)

    def fetchOrders(self, pageno, pagesize, sort, sortdir, filters):
        where, values = self.dataaccess.createFilter(filters)
        query = "SELECT p.name as product, og.id as ordergroup, side, funds, size, price, fee, to_char(o.createdat, 'MM-DD-YYYY HH24:MI:SS') as createdat FROM orders o inner join ordergroups og on og.id = o.ordergroupid inner join products p on og.productid = p.id "
        query += where
        query += " ORDER BY o.{} {} LIMIT {} OFFSET {}".format(sort,sortdir, pagesize, (pageno-1)*pagesize)
        countquery = "SELECT count(*) as totalcount from orders o inner join ordergroups og on og.id = o.ordergroupid inner join products p on p.id = og.productid " + where
        return self.dataaccess.executeRead(query, values), self.dataaccess.executeScalar(countquery, values)['totalcount']
    
    def fetchRecentOrderGroup(self, product):
        query = "SELECT id FROM ordergroups WHERE productid = (SELECT id FROM products WHERE name = %s) AND updatedat IS NULL ORDER BY createdat DESC LIMIT 1"
        ordergroup = self.dataaccess.executeScalar(query, (product,))
        if ordergroup != None:
            query = "SELECT * FROM orders WHERE ordergroupid = %s"
            orders = self.dataaccess.executeRead(query, (ordergroup['id'],))
            ordergroup['orders'] = orders
        return ordergroup

    def createOrderGroup(self, product):
        query = "INSERT INTO ordergroups (productid) VALUES ((SELECT id FROM products WHERE name = %s)) RETURNING id"
        row = self.dataaccess.executeScalar(query,(product,))
        row['orders'] = []
        return row

    def updateOrderGroup(self, ordergroupid, sellprice, totalearned, totalsize, totalfees):
        values = (sellprice, totalearned, totalsize, totalfees, ordergroupid)
        query = """UPDATE ordergroups
                        SET sellprice = %s, totalearned = %s, totalsize = %s, totalfees = %s, updatedat = now()
                    WHERE
                        id = %s"""
        self.dataaccess.execute(query, values)

    def createOrder(self, ordergroupid, side, funds, referenceid, size, price, fee):
        values = (ordergroupid, side, funds, referenceid, size, price, fee)
        query = "INSERT INTO orders (ordergroupid, side, funds, referenceid, size, price, fee) "
        query += "VALUES (%s, %s, %s, %s, %s, %s, %s)"
        self.dataaccess.execute(query, values)