import uuid
import datetime
from zoneinfo import ZoneInfo

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, func, desc
from sqlalchemy.orm import sessionmaker
from  sqlalchemy.exc import IntegrityError
import openai

from models.models import *
from config import sqlalchemy_url, OPENAI_API_KEY, ORIGINS

class BaseResponse(BaseModel):
    status: str
    message: str
    data: dict

class MatchSchema(BaseModel):
    id: uuid.UUID
    question: str
    answer: str
    color: str

class MatchResponse(BaseResponse):
    data: list[MatchSchema]

class PromptBlanksSchema(BaseModel):
    prompt: list[str]

class PromptsResponse(BaseResponse):
    data: PromptBlanksSchema

class GptAnswerSchema(BaseModel):
    gpt_response: str

class GptAnswerResponse(BaseResponse):
    data: GptAnswerSchema

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

class GptRequestSchema(BaseModel):
    prompt: list[str]
    username: str
    company: str

class InteractionSchema(BaseModel):
    request: GptRequestSchema
    datetime: datetime.datetime
    gpt_response: str

class InteractionsResponse(BaseResponse):
    data: list[InteractionSchema]

app = FastAPI()

sqlalchemy_session = sessionmaker(create_engine(sqlalchemy_url))
openai.api_key = OPENAI_API_KEY

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

REQUEST_VALIDATION_ERROR_STATUS = 422
ENTITY_ERROR_STATUS = 400


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request, exc):
    return JSONResponse(status_code=ENTITY_ERROR_STATUS,
                        content={'status': 'error', 'message': exc.errors()[0]['msg']})


@app.exception_handler(IntegrityError)
def sqlalchemy_exception_handler(request, exc):
    if 'errors.UniqueViolation' in str(exc):
        return JSONResponse(status_code=ENTITY_ERROR_STATUS,
                            content={'status': 'error', 'message': 'Duplicate unique property detected'})
    else:
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get('/api/questions')
def get_questions() -> MatchResponse:
    with sqlalchemy_session.begin() as session:
        matches = session.query(Match).all()
        matches = list(map(lambda m: MatchSchema(id=str(m.id),
                                                 question=m.question,
                                                 answer=m.answer,
                                                 color=m.color), matches))
    return {'status': 'success', 'message': 'Questions successfully retrieved', 'data': matches}

@app.put('/api/questions')
def put_questions(questions: list[MatchSchema]) -> MatchResponse:
    with sqlalchemy_session.begin() as session:
        session.query(Match).delete()
        session.add_all(map(lambda m: Match(m.id, m.question, m.answer, m.color), questions))
    return {'status': 'success', 'message': 'Questions successfully saved', 'data': questions}


@app.get('/api/prompt')
def get_prompt() -> PromptsResponse:
    with sqlalchemy_session.begin() as session:
        prompts = session.query(PromptBlank).all()
        prompts = PromptBlanksSchema(prompt=list(map(lambda q: q.text_data, prompts)))
    return {'status': 'success', 'message': 'Prompt successfully retrieved', 'data': prompts}


@app.put('/api/prompt')
def put_prompt(prompts: PromptBlanksSchema) -> PromptsResponse:
    with sqlalchemy_session.begin() as session:
        session.query(PromptBlank).delete()
        session.add_all(list(map(lambda pr: PromptBlank(uuid.UUID(hex=str(uuid.uuid4())), pr), prompts.prompt)))
    return {'status': 'success', 'message': 'Prompt successfully saved', 'data': prompts}


@app.get('/api/history')
def get_history() -> InteractionsResponse:
    with sqlalchemy_session.begin() as session:
        history = session.query(GptInteraction, func.array_agg(FilledPrompt.text_data))\
            .join(FilledPrompt).group_by(GptInteraction.id).all()
        history = list(map(lambda el: InteractionSchema(
            request=GptRequestSchema(
                prompt=el[1],
                username=el[0].username,
                company=el[0].company,
            ),
            datetime=el[0].time_happened,
            gpt_response=el[0].gpt_answer), history))
    return {'status': 'success', 'message': 'History successfully retrieved', 'data': history}


@app.post('/api/response')
def get_response(request: GptRequestSchema) -> GptAnswerResponse:
    response = openai.ChatCompletion.create(model='gpt-4', messages=[{'role': 'user', 'content': '\n'.join(request.prompt)}])
    answer = response['choices'][0]['message']['content']
    interaction_id = uuid.UUID(hex=str(uuid.uuid4()))
    with sqlalchemy_session.begin() as session:
        session.add(GptInteraction(interaction_id, answer, request.username,
                                   request.company,
                                   datetime.datetime.now(ZoneInfo('Europe/Moscow'))))
        session.flush()
        session.add_all(map(lambda pr: FilledPrompt(uuid.UUID(hex=str(uuid.uuid4())), pr, interaction_id), request.prompt))
    return {'status': 'success', 'message': 'GPT Respons successfully retrieved', 'data': {'gpt_response': answer}}

@app.get('/api/favoritePrompts')
def get_favorite_prompts() -> FavoritePromptsTimeResponse:
    with sqlalchemy_session.begin() as session:
        favorite_prompts = session.query(FavoritePrompt, func.array_agg(FavoritePromptBlank.text_data))\
            .join(FavoritePromptBlank).group_by(FavoritePrompt.id).order_by(desc(FavoritePrompt.date_added)).all()
        favorite_prompts = list(map(lambda p: FavoritePromptTimeSchema(id=p[0].id,
                                                                  title=p[0].title,
                                                                  date_added=p[0].date_added,
                                                                  prompt=p[1]), favorite_prompts))
    return {'status': 'success', 'message': 'Favorite prompts successfully retrieved', 'data': favorite_prompts}

@app.post('/api/favoritesPrompt')
def post_favorite_prompt(prompt: FavoritePromptSchema) -> FavoritePromptTimeResponse:
    with sqlalchemy_session.begin() as session:
        date_added = datetime.datetime.now(ZoneInfo('Europe/Moscow'))
        session.add(FavoritePrompt(id=prompt.id, title=prompt.title, date_added=date_added))
        session.flush()
        session.add_all(list(map(lambda p: FavoritePromptBlank(uuid.UUID(hex=str(uuid.uuid4())),
                                                          prompt.id,
                                                          p), prompt.prompt)))
    return {'status': 'success', 'message': 'Favorite prompt successfully saved', 'data':
            FavoritePromptTimeSchema(id=prompt.id, title=prompt.title, prompt=prompt.prompt, date_added=date_added)}

@app.delete('/api/favoritesPrompt')
def delete_favorite_prompt(id: uuid.UUID) -> FavoritePromptTimeResponse:
    with sqlalchemy_session.begin() as session:
        prompt = session.query(FavoritePrompt).filter_by(id=id).first()
        if prompt:
            blanks = session.query(FavoritePromptBlank.text_data).filter_by(favorite_prompt_id=id).all()
            blanks = list(map(lambda b: b[0], blanks))
            session.delete(prompt)
            return {'status': 'success', 'message': 'Favorite prompt successfully deleted', 'data':
                FavoritePromptTimeSchema(id=prompt.id, title=prompt.title, date_added=prompt.date_added, prompt=blanks)}
        else:
            return JSONResponse(status_code=ENTITY_ERROR_STATUS,
                                content={'status': 'error', 'message': "Id doesn't exist"})
