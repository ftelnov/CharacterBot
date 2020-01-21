from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *

Base = declarative_base()


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
