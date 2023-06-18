from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, UUID
from sqlalchemy.ext.declarative import declarative_base

import datetime
import uuid

from init import sql_engine

Base = declarative_base()

class PromptBlank(Base):
    def __init__(self, id: uuid.UUID, text_data: str, workspace_id: uuid.UUID):
        self.id = id
        self.text_data = text_data
        self.workspace_id = workspace_id
    __tablename__ = 'prompt_blank'
    id = Column(UUID, primary_key=True)
    text_data = Column(String, nullable=False)
    workspace_id = Column(ForeignKey('workspace.id', ondelete='cascade'), nullable=False)

class FavoritePrompt(Base):
    def __init__(self, id: uuid.UUID, title: str, date_added: datetime.datetime, workspace_id: uuid.UUID):
        self.id = id
        self.title = title
        self.date_added = date_added
        self.workspace_id = workspace_id
    __tablename__ = 'favorite_prompt'
    id = Column(UUID, primary_key=True)
    title = Column(String, nullable=False)
    date_added = Column(TIMESTAMP, nullable=False)
    workspace_id = Column(ForeignKey('workspace.id', ondelete='cascade'), nullable=False)

class FavoritePromptBlank(Base):
    def __init__(self, id: uuid.UUID, favorite_prompt_id: uuid.UUID, text_data: str):
        self.id = id
        self.favorite_prompt_id = favorite_prompt_id
        self.text_data = text_data
    __tablename__ = 'favorite_prompt_blank'
    id = Column(UUID, primary_key=True)
    favorite_prompt_id = Column(UUID, ForeignKey('favorite_prompt.id', ondelete='cascade'), nullable=False)
    text_data = Column(String)

Base.metadata.reflect(bind=sql_engine)
