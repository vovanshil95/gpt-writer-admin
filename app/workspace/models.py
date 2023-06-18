import uuid

from sqlalchemy import Column, String, UUID, BOOLEAN
from sqlalchemy.ext.declarative import declarative_base

from init import sql_engine

Base = declarative_base()

class Workspace(Base):
    def __init__(self, id: uuid.UUID, title: str, initial: bool):
        self.id = id
        self.title = title
        self.initial = initial
    __tablename__ = 'workspace'
    id = Column(UUID, primary_key=True)
    title = Column(String, nullable=False, unique=True)
    initial = Column(BOOLEAN, nullable=False)

Base.metadata.reflect(bind=sql_engine)
