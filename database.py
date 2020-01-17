from settings import *
from sqlalchemy import *


class CharactersDatabase:
    address = db_address
    engine = None
    connection = None
    metadata = None
    people = None

    def __init__(self, address):
        self.address = address
        self.engine = create_engine(self.address)
        self.connection = self.engine.connect()
        self.metadata = MetaData()

    def renew_connection(self):
        self.connection = self.engine.connect()

    def init_tables(self):
        self.people = Table('people', self.metadata, Column('id', Integer, primary_key=True), Column('name', String),
                            Column('last_name', String), Column('charisma', Integer), Column('intelligence', Integer),
                            Column('kindness', Integer), Column('seriousness', Integer), Column('sharpness'),
                            autoload=True, autoload_with=self.engine)

    def get_connection(self):
        return self.connection

    def get_engine(self):
        return self.engine
