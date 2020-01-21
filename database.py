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
        self.metadata.create_all()

    def get_connection(self):
        return self.connection

    def get_engine(self):
        return self.engine

    def get_peoples(self):
        return self.people
