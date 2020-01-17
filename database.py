from settings import *
from sqlalchemy import *


class CharactersDatabase:
    address = db_address
    engine = None
    connection = None
    metadata = None
    people = None
    message = None

    def __init__(self, address=db_address):
        self.address = address
        self.engine = create_engine(self.address)
        self.connection = self.engine.connect()
        self.metadata = MetaData(self.engine)
        self.init_tables()
        self.metadata.create_all()

    def renew_connection(self):
        self.connection = self.engine.connect()

    def init_tables(self):
        self.people = Table('people', self.metadata, Column('id', Integer, primary_key=True), Column('name', String),
                            Column('last_name', String), Column('charisma', Integer), Column('intelligence', Integer),
                            Column('kindness', Integer), Column('seriousness', Integer), Column('sharpness', Integer))
        self.message = Table('message', self.metadata, Column('id', Integer, primary_key=True),
                             Column('from_id', Integer), Column('destination_id', Integer), Column('text', String))

    def get_connection(self):
        return self.connection

    def get_engine(self):
        return self.engine

    def get_peoples(self):
        return self.people

    def get_messages(self):
        return self.message
