from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import create_engine, func, desc
from sqlalchemy.orm import sessionmaker
import openai

import uuid
import datetime
from zoneinfo import ZoneInfo

from utils import BaseResponse
from config import sqlalchemy_url, OPENAI_API_KEY
from models.models import GptInteraction, FilledPrompt, Workspace

sqlalchemy_session = sessionmaker(create_engine(sqlalchemy_url))
openai.api_key = OPENAI_API_KEY

class GptRequestSchema(BaseModel):
    prompt: list[str]
    username: str
    company: str

class GptAnswerSchema(BaseModel):
    gpt_response: str

class GptAnswerResponse(BaseResponse):
    data: GptAnswerSchema

class InteractionSchema(BaseModel):
    id: uuid.UUID
    request: GptRequestSchema
    datetime: datetime.datetime
    favorite: bool
    gpt_response: str

class InteractionsResponse(BaseResponse):
    data: list[InteractionSchema]

router = APIRouter(prefix='/api',
                   tags=['GPT Interactions'])

def get_interactions(message: str) -> InteractionsResponse:
    with sqlalchemy_session.begin() as session:
        history = session.query(GptInteraction, func.array_agg(FilledPrompt.text_data)) \
            .filter(GptInteraction.workspace_id == session.query(Workspace.id).filter(Workspace.initial).first()[0]) \
            .join(FilledPrompt).group_by(GptInteraction.id)\
            .order_by(desc(GptInteraction.time_happened))\
            .all()
        history = list(map(lambda el: InteractionSchema(
            id=el[0].id,
            request=GptRequestSchema(
                prompt=el[1],
                username=el[0].username,
                company=el[0].company,
            ),
            datetime=el[0].time_happened,
            favorite=el[0].favorite,
            gpt_response=el[0].gpt_answer), history))
    return InteractionsResponse(status='success', message=message, data=history)


@router.put('/response')
def get_response(request: GptRequestSchema) -> GptAnswerResponse:
    response = openai.ChatCompletion.create(model='gpt-4', messages=[{'role': 'user', 'content': '\n'.join(request.prompt)}])
    answer = response['choices'][0]['message']['content']
    interaction_id = uuid.UUID(hex=str(uuid.uuid4()))
    with sqlalchemy_session.begin() as session:
        session.add(GptInteraction(interaction_id, answer, request.username,
                                   request.company,
                                   datetime.datetime.now(ZoneInfo('Europe/Moscow')),
                                   session.query(Workspace.id).filter(Workspace.initial).first()[0]))
        session.flush()
        session.add_all(map(lambda pr: FilledPrompt(uuid.UUID(hex=str(uuid.uuid4())), pr, interaction_id), request.prompt))
    return GptAnswerResponse(status='success', message='GPT Response successfully retrieved', data={'gpt_response': answer})

@router.get('/history')
def get_history() -> InteractionsResponse:
    return get_interactions('History successfully retrieved')

@router.put('/favoriteHistory')
def add_to_favorite(id: uuid.UUID)->InteractionsResponse:
    with sqlalchemy_session.begin() as session:
        session.get(GptInteraction, id).favorite = True
    return get_interactions('Interaction successfully added to favorite')

@router.delete('/favoriteHistory')
def delete_from_favorite(id: uuid.UUID)->InteractionsResponse:
    with sqlalchemy_session.begin() as session:
        session.get(GptInteraction, id).favorite = False
    return get_interactions('Interaction successfully deleted from favorite')