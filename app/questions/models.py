from sqlalchemy import Column, String, ForeignKey, UUID
from sqlalchemy.ext.declarative import declarative_base

import uuid

from init import sql_engine

Base = declarative_base()

class Match(Base):
    def __init__(self, id: uuid, question: str, answer: str, color: str, workspace_id: uuid):
        self.id = id
        self.question = question
        self.answer = answer
        self.color = color
        self.workspace_id = workspace_id

    __tablename__ = 'match'
    id = Column(UUID, primary_key=True)
    question = Column(String, nullable=False)
    answer = Column(String)
    color = Column(String, nullable=False)
    workspace_id = Column(ForeignKey('workspace.id', ondelete='cascade'), nullable=False)

Base.metadata.reflect(bind=sql_engine)
