class ReportRepository():
    def __init__(self, dataaccess):
        self.dataaccess = dataaccess

    def getProductProfit(self):
        query =  '''select 
                        p.name as product,
                        sum(totalearned) - sum(totalspent) as netprofit,
                        sum(TotalEarned) - sum(TotalSpent) - sum(totalfees) as grossprofit
                    from ordergroups og
                    inner join products p on p.id = og.productid
                    where og.updatedat is not null
                    group by p.name
                    order by name'''
        return self.dataaccess.executeRead(query)