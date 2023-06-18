from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, UUID, BOOLEAN
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class GptInteraction(Base):
    __tablename__ = 'gpt_interaction'
    id = Column(UUID, primary_key=True)
    username = Column(String, nullable=False)
    company = Column(String, nullable=False)
    time_happened = Column(TIMESTAMP, nullable=False)
    favorite = Column(BOOLEAN, nullable=False, server_default='False')
    gpt_answer = Column(String, nullable=False)
    workspace_id = Column(ForeignKey('workspace.id', ondelete='cascade'), nullable=False)

class FilledPrompt(Base):
    __tablename__ = 'filled_prompt'
    id = Column(UUID, primary_key=True)
    text_data = Column(String, nullable=False)
    gpt_interaction_id = Column(UUID, ForeignKey('gpt_interaction.id', ondelete='cascade'), nullable=False)
