from fastapi import FastAPI
from pydantic import BaseModel
import openai

import os

app = FastAPI()
openai.api_key = os.environ['OPENAI_API_KEY']

class Prompt(BaseModel):
    text: str


@app.post('/api')
def get_gpt_answer(prompt: Prompt):
    response = openai.ChatCompletion.create(model='gpt-4', messages=[{'role': 'user', 'content': prompt.text}])
    answer = response['choices'][0]['message']['content']
    return {'status': 200, 'data': {'answer': answer}}
