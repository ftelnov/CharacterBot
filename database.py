from settings import *
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine(db_address)
Base = declarative_base(engine)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    extroversion = Column(Integer, default=0)
    neurotism = Column(Integer, default=0)
    lie = Column(Integer, default=0)
    stage = Column(Integer, default=0)
    stage_transferred = Column(Boolean, default=False)
    results = Column(String, default="")
    need_renew = Column(Boolean, default=False)


class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    message = Column(String, default="")
    peer_id = Column(Integer)
    checked = Column(Boolean, default=False)


temp = sessionmaker(engine)
session = temp()
Base.metadata.create_all(engine)
