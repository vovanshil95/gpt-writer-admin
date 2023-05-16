from fastapi import FastAPI
from pydantic import BaseModel
import openai

from datetime import datetime
import os

app = FastAPI()
openai.api_key = os.environ['OPENAI_API_KEY']

class Match(BaseModel):
    id: str
    question: str
    answer: str


class GptInteraction(BaseModel):
    data: list[Match]
    prompt: str
    gpt_response: str
    datetime: datetime


class HttpResponse:
    status: str
    message: str
    data: BaseModel | list | str

@app.get('api/questions')
def get_questions():
    prompt = None
    return {'status': 'success', 'message': 'Questions successfully retrieved', 'data': prompt}

@app.put('/api/questions')
def put_questions(questions: list[Match]):
    return {'status': 'success', 'message': 'Questions successfully saved', 'data': questions}


@app.get('/api/prompt')
def get_prompt():
    prompt = None
    return {'status': 'success', 'message': 'Prompt successfully retrieved', 'data': {'prompt': prompt}}


@app.put('/api/prompt')
def put_prompt(prompt: str):
    return {'status': 'success', 'message': 'Prompt successfully saved', 'prompt': prompt}


@app.get('api/history')
def get_history():
    gpt_history = None
    return {"status": "success", "message": "History successfully retrieved", 'data': gpt_history}


@app.get('/api/response')
def get_response(matches: list[Match]):
    response = openai.ChatCompletion.create(model='gpt-4', messages=[{'role': 'user', 'content':
        '\n\n'.join(lambda m: f'{m.question}: {m.answer}'.aprompt.matches)}])
    answer = response['choices'][0]['message']['content']

    return {'status': 'success', 'message': 'Questions successfully retrieved', 'data': answer}