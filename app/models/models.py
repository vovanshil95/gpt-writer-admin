import dataclasses

from sqlalchemy import MetaData, Table, Column, String, TIMESTAMP, ForeignKey, UUID, BOOLEAN
from sqlalchemy.orm import registry

import datetime
import uuid

metadata = MetaData()
mapper_registry = registry()

class Match:
    def __init__(self, id: uuid.UUID, question: str, answer: str, color: str, workspace_id: uuid.UUID):
        self.id = id
        self.question = question
        self.answer = answer
        self.color = color
        self.workspace_id = workspace_id

class PromptBlank:
    def __init__(self, id: uuid.UUID, text_data: str, workspace_id: uuid.UUID):
        self.id = id
        self.text_data = text_data
        self.workspace_id = workspace_id


class FilledPrompt:
    def __init__(self, id: uuid.UUID, text_data: str, gpt_interaction_id: UUID):
        self.id = id
        self.text_data = text_data
        self.gpt_interaction_id = gpt_interaction_id

class GptInteraction:
    def __init__(self, id: uuid.UUID, gpt_answer: str, username: str, company: str, time_happened: datetime.datetime, workspace_id: uuid.UUID):
        self.id = id
        self.gpt_answer = gpt_answer
        self.username = username
        self.company = company
        self.time_happened = time_happened
        self.workspace_id = workspace_id


class FavoritePrompt:
    def __init__(self, id: uuid.UUID, title: str, date_added: datetime.datetime, workspace_id: uuid.UUID):
        self.id = id
        self.title = title
        self.date_added = date_added
        self.workspace_id = workspace_id

class FavoritePromptBlank:
    def __init__(self, id: uuid.UUID, favorite_prompt_id: UUID, text_data: str):
        self.id = id
        self.favorite_prompt_id = favorite_prompt_id
        self.text_data = text_data

class Workspace:
    def __init__(self, id: uuid.UUID, title: str, initial: bool):
        self.id = id,
        self.title = title
        self.initial = initial


match = Table('match',
                 metadata,
                 Column('id', UUID, primary_key=True),
                 Column('question', String, nullable=False),
                 Column('answer', String),
                 Column('color', String, nullable=False),
                 Column('workspace_id', ForeignKey('workspace.id', ondelete='cascade'), nullable=False),)

prompt_blank = Table('prompt_blank',
               metadata,
               Column('id', UUID, primary_key=True),
               Column('text_data', String, nullable=False),
               Column('workspace_id', ForeignKey('workspace.id', ondelete='cascade'), nullable=False),)

gpt_interaction = Table('gpt_interactions',
                        metadata,
                        Column('id', UUID, primary_key=True),
                        Column('username', String, nullable=False),
                        Column('company', String, nullable=False),
                        Column('time_happened', TIMESTAMP, nullable=False),
                        Column('favorite', BOOLEAN, nullable=False, server_default='False'),
                        Column('gpt_answer', String, nullable=False),
                        Column('workspace_id', ForeignKey('workspace.id', ondelete='cascade'), nullable=False),)

filled_prompt = Table('filled_prompt',
               metadata,
               Column('id', UUID, primary_key=True),
               Column('text_data', String, nullable=False),
               Column('gpt_interaction_id', UUID, ForeignKey('gpt_interactions.id', ondelete='cascade'), nullable=False),)

favorite_prompt = Table('favorite_prompt',
                        metadata,
                        Column('id', UUID, primary_key=True),
                        Column('title', String, nullable=False),
                        Column('date_added', TIMESTAMP, nullable=False),
                        Column('workspace_id', ForeignKey('workspace.id', ondelete='cascade'), nullable=False),)

favorite_prompt_blank = Table('favorite_prompt_blank',
                              metadata,
                              Column('id', UUID, primary_key=True),
                              Column('favorite_prompt_id', UUID, ForeignKey('favorite_prompt.id', ondelete='cascade'), nullable=False),
                              Column('text_data', String),)

workspace = Table('workspace',
                  metadata,
                  Column('id', UUID, primary_key=True),
                  Column('title', String, nullable=False, unique=True),
                  Column('initial', BOOLEAN, nullable=False),)

mapper_registry.map_imperatively(Match, match)
mapper_registry.map_imperatively(PromptBlank, prompt_blank)
mapper_registry.map_imperatively(GptInteraction, gpt_interaction)
mapper_registry.map_imperatively(FilledPrompt, filled_prompt)
mapper_registry.map_imperatively(FavoritePrompt, favorite_prompt)
mapper_registry.map_imperatively(FavoritePromptBlank, favorite_prompt_blank)
mapper_registry.map_imperatively(Workspace, workspace)
