import logging

class DbLogHandler(logging.Handler):
    def __init__(self, dbaccess):
        logging.Handler.__init__(self)
        self.db = dbaccess

    def emit(self, record):
        self.db.createLog(record.name, record.levelno, record.filename, record.lineno, record.msg)
