class OrdersRepository():
    def __init__(self, dataaccess):
        self.dataaccess = dataaccess
        
    def createOrder(self, product, side, referenceid, size, price, fee):
        values = (product, side, referenceid, size, price, fee)
        query = "INSERT INTO orders (productid, side, referenceid, size, price, fee) "
        query += "VALUES ((select id from product where name = %s), %s, %s, %s, %s, %s)"
        self.dataaccess.execute(values)