from pydantic import BaseModel

import uuid
import datetime

from utils import BaseResponse

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
