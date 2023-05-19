from sqlalchemy import MetaData, Table, Column, String, TIMESTAMP, ForeignKey, UUID
from sqlalchemy.orm import registry

import datetime
import uuid

metadata = MetaData()

mapper_registry = registry()

class Question:
    def __init__(self, id: uuid.UUID, text_data: str):
        self.id = id
        self.text_data = text_data

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

class QuestionPromptBlank:
    def __init__(self, question_id: uuid.UUID, prompt_blank_id: uuid.UUID):
        self.question_id = question_id
        self.prompt_blank_id = prompt_blank_id

question = Table('question',
                 metadata,
                 Column('id', UUID, primary_key=True),
                 Column('text_data', String, nullable=False),)

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

question_prompt_blank = Table('question_prompt_blank',
                              metadata,
                              Column('question_id', UUID, ForeignKey('question.id'), primary_key=True),
                              Column('prompt_blank_id', UUID, ForeignKey('prompt_blank.id'), primary_key=True),)


mapper_registry.map_imperatively(Question, question)
mapper_registry.map_imperatively(PromptBlank, prompt_blank)
mapper_registry.map_imperatively(GptInteraction, gpt_interaction)
mapper_registry.map_imperatively(FilledPrompt, filled_prompt)
mapper_registry.map_imperatively(QuestionPromptBlank, question_prompt_blank)
