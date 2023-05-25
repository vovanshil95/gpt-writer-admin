import uuid

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
import openai

from models.models import *
from config import sqlalchemy_url, OPENAI_API_KEY

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

class PromptsSchema(BaseModel):
    prompt: list[str]
class PromptsResponse(BaseResponse):
    data: PromptsSchema

class InteractionSchema(BaseModel):
    prompt: list[str]
    gpt_response: str
    datetime: datetime.datetime

class InteractionsResponse(BaseResponse):
    data: list[InteractionSchema]

class GptAnswerSchema(BaseModel):
    gpt_response: str

class GptAnswerResponse(BaseResponse):
    data: GptAnswerSchema

class FavoritePromptShema(BaseModel):
    id: uuid.UUID
    title: str
    prompt: list[str]

class FavoritePromptResponse(BaseResponse):
    data: list[FavoritePromptShema]

app = FastAPI()

sqlalchemy_session = sessionmaker(create_engine(sqlalchemy_url))
openai.api_key = OPENAI_API_KEY

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

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
        prompts = PromptsSchema(prompt=list(map(lambda q: q.text_data, prompts)))
    return {'status': 'success', 'message': 'Prompt successfully retrieved', 'data': prompts}


@app.put('/api/prompt')
def put_prompt(prompts: PromptsSchema) -> PromptsResponse:
    with sqlalchemy_session.begin() as session:
        session.query(PromptBlank).delete()
        session.add_all(list(map(lambda pr: PromptBlank(uuid.UUID(hex=str(uuid.uuid4())), pr), prompts.prompt)))
    return {'status': 'success', 'message': 'Prompt successfully saved', 'data': prompts}


@app.get('/api/history')
def get_history() -> InteractionsResponse:
    with sqlalchemy_session.begin() as session:
        history = session.query(GptInteraction, func.array_agg(FilledPrompt.text_data))\
            .join(FilledPrompt).group_by(GptInteraction.id).all()
        history = list(map(lambda el: InteractionSchema(prompt=el[1],
                                                        gpt_response=el[0].gpt_answer,
                                                        datetime=el[0].time_happened), history))
    return {"status": "success", "message": "History successfully retrieved", 'data': history}


@app.post('/api/response')
def get_response(prompts: list[str]) -> GptAnswerResponse:
    response = openai.ChatCompletion.create(model='gpt-4', messages=[{'role': 'user', 'content': '\n'.join(prompts)}])
    answer = response['choices'][0]['message']['content']
    interaction_id = uuid.UUID(hex=str(uuid.uuid4()))
    with sqlalchemy_session.begin() as session:
        session.add(GptInteraction(interaction_id, answer, datetime.datetime.now()))
        session.flush()
        session.add_all(map(lambda pr: FilledPrompt(uuid.UUID(hex=str(uuid.uuid4())), pr, interaction_id), prompts))
    return {'status': 'success', 'message': 'GPT Respons successfully retrieved', 'data': {'gpt_response': answer}}

@app.get('/api/favoritesPrompts')
def get_favorite_prompts() -> FavoritePromptResponse:
    with sqlalchemy_session.begin() as session:
        favorite_prompts = session.query(FavoritePrompt, func.array_agg(FavoritePromptBlank.text_data))\
            .join(FavoritePromptBlank).group_by(FavoritePrompt.id).all()
        favorite_prompts = list(map(lambda p: FavoritePromptShema(id=p[0].id,
                                                                  title=p[0].title,
                                                                  prompt=p[1]), favorite_prompts))
    return {'status': 'success', 'message': 'Favorite prompts successfully retrieved', 'data': favorite_prompts}

@app.post('/api/favoritesPrompts')
def post_favorite_prompts(prompts: list[FavoritePromptShema]) -> FavoritePromptResponse:
    with sqlalchemy_session.begin() as session:
        session.add_all(map(lambda p: FavoritePrompt(id=p.id, title=p.title), prompts))
        session.flush()
        prompt_blanks = []
        for p in prompts:
            prompt_blanks.extend([FavoritePromptBlank(id=uuid.UUID(hex=str(uuid.uuid4())),
                                                         favorite_prompt_id=pb[0],
                                                         text_data=pb[1])
                                     for pb in zip([p.id] * len(p.prompt), p.prompt)])
        session.add_all(prompt_blanks)
    return {'status': 'success', 'message': 'Favorite prompts successfully saved', 'data': prompts}
