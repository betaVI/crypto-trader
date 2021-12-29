import logging

class DbLogHandler(logging.Handler):
    def __init__(self, logrepo):
        logging.Handler.__init__(self)
        self.db = logrepo

    def emit(self, record):
        self.db.createLog(record.name, record.levelno, record.levelname, record.filename, record.lineno, record.msg)
