class LogsRepository():
    def __init__(self, dataaccess):
        self.dataaccess = dataaccess
    
    def createLog(self, loggername, loglevel, loglevelname, filename, lineno, message):
        values = (loggername, loglevel, loglevelname, filename, lineno, message)
        query = ','.join(['%s']*len(values))
        query = "INSERT INTO traderlogs (loggername, loglevel, loglevelname, filename, lineno, message) VALUES ({})".format(query)
        error = self.dataaccess.execute(query, values)
        if error != None:
            print('Log Entry error: ' + error)
        
    def getLoggers(self):
        query = "SELECT distinct loggername from traderlogs"
        return self.dataaccess.executeRead(query)
    
    def fetchLogs(self, pageno, pagesize, sort, sortdir, filters):
        where, values = self.dataaccess.createFilter(filters)
        logquery = "SELECT id, loggername, loglevelname, filename, lineno, message, to_char(createdat, 'MM-DD-YY HH24:MI:SS.MS') as createdat FROM traderlogs {} ORDER BY {} {} LIMIT {} OFFSET {}".format(where,sort,sortdir,pagesize,(pageno-1)*pagesize)
        pagequery = "SELECT count(*) as totalcount FROM traderlogs " + where
        logs = self.dataaccess.executeRead(logquery,values)
        count = self.dataaccess.executeRead(pagequery, values)
        return logs,count[0]['totalcount']

    def purgeLogs(self):
        query = "DELETE from traderlogs where createdat < now() - interval '60 days'"
        self.dataaccess.execute(query)