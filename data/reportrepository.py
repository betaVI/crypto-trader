class ReportRepository():
    def __init__(self, dataaccess):
        self.dataaccess = dataaccess

    def getProductProfit(self):
        query =  '''select 
                        p.name as product,
                        round(sum(totalearned) - sum(totalspent), 4) as netprofit,
                        round(sum(TotalEarned) - sum(TotalSpent) - sum(totalfees), 4) as grossprofit
                    from ordergroups og
                    inner join products p on p.id = og.productid
                    where og.updatedat > current_date - 90
                    group by p.name
                    order by name'''
        return self.dataaccess.executeRead(query)