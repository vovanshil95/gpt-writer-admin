from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, UUID, BOOLEAN, Integer
from sqlalchemy.ext.declarative import declarative_base

import datetime
import uuid

from init import sql_engine

Base = declarative_base()

class GptInteraction(Base):
    def __init__(self,
                 id: uuid.UUID,
                 username: str,
                 company: str,
                 time_happened: datetime.datetime,
                 favorite: bool,
                 gpt_answer: str,
                 workspace_id: uuid.UUID):
        self.id = id
        self.username = username
        self.company = company
        self.time_happened = time_happened
        self.favorite = favorite
        self.gpt_answer = gpt_answer
        self.workspace_id = workspace_id
    __tablename__ = 'gpt_interaction'
    id = Column(UUID, primary_key=True)
    username = Column(String, nullable=False)
    company = Column(String, nullable=False)
    time_happened = Column(TIMESTAMP, nullable=False)
    favorite = Column(BOOLEAN, nullable=False, server_default='False')
    gpt_answer = Column(String, nullable=False)
    workspace_id = Column(ForeignKey('workspace.id', ondelete='cascade'), nullable=False)

class FilledPrompt(Base):
    def __init__(self, id: uuid.UUID, text_data: str, gpt_interaction_id: uuid.UUID, number: int):
        self.id = id
        self.text_data = text_data
        self.gpt_interaction_id = gpt_interaction_id
        self.number = number
    __tablename__ = 'filled_prompt'
    id = Column(UUID, primary_key=True)
    text_data = Column(String, nullable=False)
    gpt_interaction_id = Column(UUID, ForeignKey('gpt_interaction.id', ondelete='cascade'), nullable=False)
    number = Column(Integer, nullable=False)

Base.metadata.reflect(bind=sql_engine)
