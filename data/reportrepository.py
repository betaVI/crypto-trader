class ReportRepository():
    def __init__(self, dataaccess):
        self.dataaccess = dataaccess

    def getProductProfit(self):
        query =  '''select 
                        p.name as product,
                        to_char(og.updatedat, 'MM/YYYY') as month,
                        round(sum(totalearned) - sum(totalspent), 4) as netprofit,
                        round(sum(TotalEarned) - sum(TotalSpent) - sum(totalfees), 4) as grossprofit
                    from ordergroups og
                    inner join products p on p.id = og.productid
                    where og.updatedat > current_date - 180
                    group by p.name, to_char(og.updatedat, 'MM/YYYY')
                    order by name'''
        return self.dataaccess.executeRead(query)