from sqlalchemy import Column, String, UUID, BOOLEAN
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Workspace(Base):
    __tablename__ = 'workspace'
    id = Column(UUID, primary_key=True)
    title = Column(String, nullable=False, unique=True)
    initial = Column(BOOLEAN, nullable=False)
