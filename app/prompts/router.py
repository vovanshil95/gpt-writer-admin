from fastapi import APIRouter
from sqlalchemy import func, desc

import datetime
import uuid
from zoneinfo import ZoneInfo

from workspace.models import Workspace
from prompts.models import PromptBlank, FavoritePromptBlank, FavoritePrompt
from init import sqlalchemy_session
from prompts.schemas import\
    FavoritePromptsTimeResponse,\
    FavoritePromptTimeSchema,\
    PromptsResponse,\
    FavoritePromptSchema,\
    PromptBlanksSchema,\
    FavoritePromptTimeResponse

router = APIRouter(prefix='/api',
                   tags=['Prompts'])

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
        session.add_all(list(map(lambda pr: PromptBlank(id=uuid.UUID(hex=str(uuid.uuid4())),
                                                        text_data=pr,
                                                        workspace_id=workspace_id),
                                 prompts.prompt)))
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
        session.add_all(list(map(lambda p: FavoritePromptBlank(id=uuid.UUID(hex=str(uuid.uuid4())),
                                                               favorite_prompt_id=prompt.id,
                                                               text_data=p),
                                 prompt.prompt)))
        favorite_prompt = FavoritePromptTimeSchema(id=prompt.id, title=prompt.title, prompt=prompt.prompt, date_added=date_added)
    return FavoritePromptTimeResponse(status='success', message='Favorite prompt successfully saved', data=favorite_prompt)

@router.delete('/favoritePrompts')
def delete_favorite_prompts(id: uuid.UUID) -> FavoritePromptsTimeResponse:
    with sqlalchemy_session.begin() as session:
        prompt = session.get(FavoritePrompt, id)
        if not prompt: raise AttributeError("Id doesn't exist")
        session.delete(prompt)
    return get_favorite_prompts_('Favorite prompt successfully deleted')
