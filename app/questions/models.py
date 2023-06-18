from sqlalchemy import Column, String, ForeignKey, UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Match(Base):
    __tablename__ = 'match'
    id = Column(UUID, primary_key=True)
    question = Column(String, nullable=False)
    answer = Column(String)
    color = Column(String, nullable=False)
    workspace_id = Column(ForeignKey('workspace.id', ondelete='cascade'), nullable=False)
