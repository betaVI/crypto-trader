class LogsRepository():
    def __init__(self, dataaccess):
        self.dataaccess = dataaccess
    
    def createLog(self, loggername, loglevel, loglevelname, filename, lineno, message):
        query = "INSERT INTO traderlogs (loggername, loglevel, loglevelname, filename, lineno, message) VALUES ('{}',{},'{}','{}',{},'{}')".format(loggername, loglevel, loglevelname, filename, lineno, message)
        error = self.dataaccess.execute(query)
        if error != None:
            print('Log Entry error: ' + error)
        
    def fetchLogs(self, pageno, pagesize, sort, sortdir):
        logquery = "SELECT id, loggername, loglevelname, filename, lineno, message, to_char(createdat, 'MM-DD-YYYY HH24:MI:SS') as createdat FROM traderlogs ORDER BY {} {} LIMIT {} OFFSET {}".format(sort,sortdir,pagesize,(pageno-1)*pagesize)
        pagequery = "SELECT count(*) as totalcount FROM traderlogs"
        return self.dataaccess.executeRead(logquery),self.dataaccess.executeRead(pagequery)[0]['totalcount']