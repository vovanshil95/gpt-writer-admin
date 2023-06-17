from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import create_engine, func, desc
from sqlalchemy.orm import sessionmaker

import datetime
import uuid
from zoneinfo import ZoneInfo

from config import sqlalchemy_url
from utils import BaseResponse
from models.models import PromptBlank, Workspace, FavoritePromptBlank, FavoritePrompt

router = APIRouter(prefix='/api',
                   tags=['Prompts'])

sqlalchemy_session = sessionmaker(create_engine(sqlalchemy_url))

class PromptBlanksSchema(BaseModel):
    prompt: list[str]

class PromptsResponse(BaseResponse):
    data: PromptBlanksSchema

class FavoritePromptSchema(BaseModel):
    id: uuid.UUID
    title: str
    prompt: list[str]

class FavoritePromptTimeSchema(FavoritePromptSchema):
    date_added: datetime.datetime

class FavoritePromptsTimeResponse(BaseResponse):
    data: list[FavoritePromptTimeSchema]

class FavoritePromptResponse(BaseResponse):
    data: FavoritePromptSchema

class FavoritePromptTimeResponse(BaseResponse):
    data: FavoritePromptTimeSchema

def get_favorite_prompts_(message: str) -> FavoritePromptsTimeResponse:
    with sqlalchemy_session.begin() as session:
        favorite_prompts = session.query(FavoritePrompt, func.array_agg(FavoritePromptBlank.text_data))\
            .filter(FavoritePrompt.workspace_id == session.query(Workspace.id).filter(Workspace.initial).first()[0]) \
            .join(FavoritePromptBlank).group_by(FavoritePrompt.id).order_by(desc(FavoritePrompt.date_added)).all()
        favorite_prompts = list(map(lambda p: FavoritePromptTimeSchema(id=p[0].id,
                                                                  title=p[0].title,
                                                                  date_added=p[0].date_added,
                                                                  prompt=p[1]), favorite_prompts))
    return FavoritePromptsTimeResponse(status='success', message=message, data=favorite_prompts)

@router.get('/prompt')
def get_prompt() -> PromptsResponse:
    with sqlalchemy_session.begin() as session:
        prompts = session.query(PromptBlank) \
            .filter(PromptBlank.workspace_id == session.query(Workspace.id).filter(Workspace.initial).first()[0]) \
            .all()
        prompts = PromptBlanksSchema(prompt=list(map(lambda q: q.text_data, prompts)))
    return PromptsResponse(status='success', message='Prompt successfully retrieved', data=prompts)

@router.put('/prompt')
def put_prompt(prompts: PromptBlanksSchema) -> PromptsResponse:
    with sqlalchemy_session.begin() as session:
        workspace_id = session.query(Workspace.id).filter(Workspace.initial).first()[0]
        session.query(PromptBlank).filter(PromptBlank.workspace_id == workspace_id).delete()
        session.add_all(list(map(lambda pr: PromptBlank(uuid.UUID(hex=str(uuid.uuid4())), pr, workspace_id), prompts.prompt)))
    return PromptsResponse(status='success', message='Prompt successfully saved', data=prompts)


@router.get('/favoritePrompts')
def get_favorite_prompts() -> FavoritePromptsTimeResponse:
    return get_favorite_prompts_('Favorite prompts successfully retrieved')

@router.put('/favoritePrompts')
def put_favorite_prompts(prompt: FavoritePromptSchema) -> FavoritePromptTimeResponse:
    with sqlalchemy_session.begin() as session:
        date_added = datetime.datetime.now(ZoneInfo('Europe/Moscow'))
        session.add(FavoritePrompt(id=prompt.id,
                                   title=prompt.title,
                                   date_added=date_added,
                                   workspace_id=session.query(Workspace.id).filter(Workspace.initial).first()[0]))
        session.flush()
        session.add_all(list(map(lambda p: FavoritePromptBlank(uuid.UUID(hex=str(uuid.uuid4())), prompt.id, p), prompt.prompt)))
        favorite_prompt = FavoritePromptTimeSchema(id=prompt.id, title=prompt.title, prompt=prompt.prompt, date_added=date_added)
    return FavoritePromptTimeResponse(status='success', message='Favorite prompt successfully saved', data=favorite_prompt)

@router.delete('/favoritePrompts')
def delete_favorite_prompts(id: uuid.UUID) -> FavoritePromptsTimeResponse:
    with sqlalchemy_session.begin() as session:
        prompt = session.get(FavoritePrompt, id)
        if not prompt: raise AttributeError("Id doesn't exist")
        session.delete(prompt)
    return get_favorite_prompts_('Favorite prompt successfully deleted')
