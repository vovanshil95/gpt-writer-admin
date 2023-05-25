from sqlalchemy import MetaData, Table, Column, String, TIMESTAMP, ForeignKey, UUID
from sqlalchemy.orm import registry

import datetime
import uuid

metadata = MetaData()
mapper_registry = registry()

class Match:
    def __init__(self, id: uuid.UUID, question: str, answer: str, color: str):
        self.id = id
        self.question = question
        self.answer = answer
        self.color = color

class PromptBlank:
    def __init__(self, id: uuid.UUID, text_data: str):
        self.id = id
        self.text_data = text_data

class FilledPrompt:
    def __init__(self, id: uuid.UUID, text_data: str, gpt_interaction_id: UUID):
        self.id = id
        self.text_data = text_data
        self.gpt_interaction_id = gpt_interaction_id

class GptInteraction:
    def __init__(self, id: uuid.UUID, gpt_answer: str, time_happened: datetime.datetime):
        self.id = id
        self.gpt_answer = gpt_answer
        self.time_happened = time_happened

class MatchPromptBlank:
    def __init__(self, match_id: uuid.UUID, prompt_blank_id: uuid.UUID):
        self.match_id = match_id
        self.prompt_blank_id = prompt_blank_id

class FavoritePrompt:
    def __init__(self, id: UUID, title: str):
        self.id = id
        self.title = title

class FavoritePromptBlank:
    def __init__(self, id: UUID, favorite_prompt_id: UUID, text_data: str):
        self.id = id
        self.favorite_prompt_id = favorite_prompt_id
        self.text_data = text_data

match = Table('match',
                 metadata,
                 Column('id', UUID, primary_key=True),
                 Column('question', String, nullable=False),
                 Column('answer', String),
                 Column('color', String, nullable=False),)

prompt_blank = Table('prompt_blank',
               metadata,
               Column('id', UUID, primary_key=True),
               Column('text_data', String, nullable=False),)

gpt_interaction = Table('gpt_interaction',
                        metadata,
                        Column('id', UUID, primary_key=True),
                        Column('gpt_answer', String, nullable=False),
                        Column('time_happened', TIMESTAMP, nullable=False),)

filled_prompt = Table('filled_prompt',
               metadata,
               Column('id', UUID, primary_key=True),
               Column('text_data', String, nullable=False),
               Column('gpt_interaction_id', UUID, ForeignKey('gpt_interaction.id'), nullable=False),)

favorite_prompt = Table('favorite_prompt',
                        metadata,
                        Column('id', UUID, primary_key=True),
                        Column('title', String, nullable=False),)

favorite_prompt_blank = Table('favorite_prompt_blank',
                              metadata,
                              Column('id', UUID, primary_key=True),
                              Column('favorite_prompt_id', UUID, ForeignKey('favorite_prompt.id')),
                              Column('text_data', String),)

mapper_registry.map_imperatively(Match, match)
mapper_registry.map_imperatively(PromptBlank, prompt_blank)
mapper_registry.map_imperatively(GptInteraction, gpt_interaction)
mapper_registry.map_imperatively(FilledPrompt, filled_prompt)
mapper_registry.map_imperatively(FavoritePrompt, favorite_prompt)
mapper_registry.map_imperatively(FavoritePromptBlank, favorite_prompt_blank)
