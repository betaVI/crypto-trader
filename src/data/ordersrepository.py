import logging
from src.data.dataaccess import DataAccess

class OrdersRepository():
    def __init__(self, dataaccess: DataAccess):
        self.dataaccess = dataaccess
        self.logger = logging.getLogger('OrderRepository')

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
        query = "SELECT id FROM ordergroups WHERE productid = (SELECT id FROM products WHERE name = %s and exchangeid = %s) AND updatedat IS NULL ORDER BY createdat DESC LIMIT 1"
        ordergroup = self.dataaccess.executeScalar(query, (product,1))
        if ordergroup != None:
            query = "SELECT * FROM orders WHERE ordergroupid = %s"
            orders = self.dataaccess.executeRead(query, (ordergroup['id'],))
            ordergroup['orders'] = orders
        return ordergroup

    def createOrderGroup(self, product):
        query = "INSERT INTO ordergroups (productid) VALUES ((SELECT id FROM products WHERE name = %s and exchangeid = %s)) RETURNING id"
        row = self.dataaccess.executeScalar(query,(product,1))
        row['orders'] = []
        return row

    def updateOrderGroup(self, referenceid, ordergroupid, sellprice, totalearned, totalsize, totalfees):
        self.logger.debug('Update Order Group ({}) [{}]: earned {} = (${} * {}) - ${}'.format(ordergroupid, referenceid, totalearned, sellprice, totalsize, totalfees))
        values = (sellprice, totalearned, totalsize, totalfees, ordergroupid)
        query =  """UPDATE ordergroups og
                    SET 
                        saleprice = %s, 
                        totalearned = %s, 
                        totalsize = %s, 
                        totalfees = o.fee + %s, 
                        totalspent = o.funds, 
                        updatedat = now()
                    FROM
                        (SELECT ordergroupid, sum(funds) as funds, sum(fee) as fee from orders where side = 'buy' group by ordergroupid) o
                    WHERE
                        o.ordergroupid = og.id
                    and og.id = %s"""
        
        self.logger.debug('QUERY: {}'.format(query))
        error = self.dataaccess.execute(query, values)

        if error is not None:
            self.logger.error('Update Order Group ERROR: {}'.format(error))

        self.createOrder(ordergroupid, 'sell', totalearned, referenceid, totalsize, sellprice, totalfees)

    def createOrder(self, ordergroupid, side, funds, referenceid, size, price, fee):
        self.logger.debug('Create Order ({}): [{}] ${} = (${} * {}) + {}'.format(ordergroupid, side, funds, price, size, fee))
        values = (ordergroupid, side, funds, referenceid, size, price, fee)
        query = "INSERT INTO orders (ordergroupid, side, funds, referenceid, size, price, fee) "
        query += "VALUES (%s, %s, %s, %s, %s, %s, %s)"

        error = self.dataaccess.execute(query, values)

        if error is not None:
            self.logger.error('Update Order Group ERROR: {}'.format(error))