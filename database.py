from settings import *
from sqlalchemy import *
from sqlalchemy.orm import *


class CharactersDatabase:
    address = db_address
    engine = None
    connection = None
    metadata = None
    people = None
    message = None
    people_stage = None
    ideal_people = None
    session = None

    def __init__(self, address=db_address):
        self.address = address
        self.engine = create_engine(self.address)
        self.connection = self.engine.connect()
        self.metadata = MetaData(self.engine)
        session = sessionmaker(self.engine)
        self.session = session()
        self.init_tables()
        self.metadata.create_all()

    def renew_connection(self):
        self.connection = self.engine.connect()

    def init_tables(self):
        self.people = Table('people', self.metadata, Column('user_id', Integer, primary_key=True), Column('name', String),
                            Column('last_name', String), Column('charisma', Integer, default=5),
                            Column('intelligence', Integer, default=5),
                            Column('kindness', Integer, default=5), Column('seriousness', Integer, default=5),
                            Column('sharpness', Integer, default=5))
        self.message = Table('message', self.metadata, Column('id', Integer, primary_key=True),
                             Column('from_id', Integer), Column('destination_id', Integer), Column('text', String))
        self.people_stage = Table('people_stage', self.metadata, Column('user_id', Integer, primary_key=True),
                                  Column('stage', Integer))
        self.ideal_people = Table('ideal_people', self.metadata, Column('user_id', Integer, primary_key=True),
                                  Column('charisma', Integer, default=5), Column('intelligence', Integer, default=5),
                                  Column('kindness', Integer, default=5), Column('seriousness', Integer, default=5),
                                  Column('sharpness', Integer, default=5))

    def get_connection(self):
        return self.connection

    def get_engine(self):
        return self.engine

    def get_peoples(self):
        return self.people

    def get_messages(self):
        return self.message
