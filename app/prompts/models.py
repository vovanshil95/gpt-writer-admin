from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class PromptBlank(Base):
    __tablename__ = 'prompt_blank'
    id = Column(UUID, primary_key=True)
    text_data = Column(String, nullable=False)
    workspace_id = Column(ForeignKey('workspace.id', ondelete='cascade'), nullable=False)

class FavoritePrompt(Base):
    __tablename__ = 'favorite_prompt'
    id = Column(UUID, primary_key=True)
    title = Column(String, nullable=False)
    date_added = Column(TIMESTAMP, nullable=False)
    workspace_id = Column(ForeignKey('workspace.id', ondelete='cascade'), nullable=False)

class FavoritePromptBlank(Base):
    __tablename__ = 'favorite_prompt_blank'
    id = Column(UUID, primary_key=True)
    favorite_prompt_id = Column(UUID, ForeignKey('favorite_prompt.id', ondelete='cascade'), nullable=False)
    text_data = Column(String)
