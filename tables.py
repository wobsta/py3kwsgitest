import sqlalchemy

metadata = sqlalchemy.MetaData()

log_table = sqlalchemy.Table('log', metadata,
                             sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
                             sqlalchemy.Column('filename', sqlalchemy.Unicode),
                             sqlalchemy.Column('digest', sqlalchemy.Unicode),
                             sqlalchemy.Column('comment', sqlalchemy.Unicode),
                             sqlalchemy.Column('user_agent', sqlalchemy.Unicode),
                             sqlalchemy.Column('traceback', sqlalchemy.Unicode))

def init(engine):
    metadata.create_all(bind=engine)
