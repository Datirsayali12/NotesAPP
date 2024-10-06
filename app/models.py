from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, DateTime, Integer
import datetime

def get_timestamp():
    return datetime.datetime.now()

BASE=declarative_base()
#declarative_base() is a function in SQLAlchemy that returns a base class.
# This base class serves as a foundation for all your ORM (Object-Relational Mapping) models.
#create model



class Todo(BASE):
    __tablename__ = 'to_do'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    notes = Column(String)
    timestamp = Column(DateTime, default=get_timestamp())

    def __init__(self, title: str, notes: str):
        self.title = title
        self.notes = notes






