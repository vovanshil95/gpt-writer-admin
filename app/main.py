from fastapi import FastAPI
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

class QuestionSchema(BaseModel):
    id: uuid.UUID
    question: str
class ResponseQuestions(BaseResponse):
    data: list[QuestionSchema]

class PromptsSchema(BaseModel):
    prompt: list[str]
class ResponsePrompts(BaseResponse):
    data: PromptsSchema

class InteractionSchema(BaseModel):
    prompts: list[str]
    gpt_response: str
    datetime: datetime.datetime

class InteractionsResponse(BaseResponse):
    data: list[InteractionSchema]

class GptAnswerSchema(BaseModel):
    gpt_response: str

class GptAnswerResponse(BaseResponse):
    data: GptAnswerSchema

app = FastAPI()

sqlalchemy_session = sessionmaker(create_engine(sqlalchemy_url))
openai.api_key = OPENAI_API_KEY

@app.get('/api/questions')
def get_questions():
    with sqlalchemy_session.begin() as session:
        questions = session.query(Question).all()
        questions = list(map(lambda q: {'id': str(q.id), 'text_data': q.text_data}, questions))
    print({'status': 'success', 'message': 'Questions successfully retrieved', 'data': questions})
    return {'status': 'success', 'message': 'Questions successfully retrieved', 'data': questions}

@app.put('/api/questions')
def put_questions(questions: list[QuestionSchema]) -> ResponseQuestions:
    with sqlalchemy_session.begin() as session:
        session.add_all(map(lambda q: Question(q.id, q.question), questions))
    return {'status': 'success', 'message': 'Questions successfully saved', 'data': questions}


@app.get('/api/prompt')
def get_prompt():
    with sqlalchemy_session.begin() as session:
        prompts = session.query(PromptBlank).all()
        prompts = list(map(lambda q: {'id': q.id, 'text_data': q.text_data}, prompts))
    return {'status': 'success', 'message': 'Prompt successfully retrieved', 'data': {'prompt': prompts}}


@app.put('/api/prompt')
def put_prompt(prompts: list[str]):
    with sqlalchemy_session.begin() as session:
        session.add_all(list(map(lambda pr: PromptBlank(uuid.UUID(hex=str(uuid.uuid4())), pr), prompts)))
    return {'status': 'success', 'message': 'Prompt successfully saved', 'prompt': prompts}


@app.get('/api/history')
def get_history():
    with sqlalchemy_session.begin() as session:
        history = session.query(GptInteraction, func.array_agg(FilledPrompt.text_data))\
            .join(FilledPrompt).group_by(GptInteraction.id).all()
        history = list(map(lambda el: {'prompt': el[1],
                                       'gpr_response': el[0].gpt_answer,
                                       'datetime': el[0].time_happened}, history))
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
