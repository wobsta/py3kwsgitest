import sqlalchemy.orm
import tables

class Log(object):

    def __init__(self, filename, digest, comment, user_agent, traceback):
        self.filename = filename
        self.digest = digest
        self.comment = comment
        self.user_agent = user_agent
        self.traceback = traceback

sqlalchemy.orm.mapper(Log, tables.log_table)
