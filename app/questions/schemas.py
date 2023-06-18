from pydantic import BaseModel

import uuid

from utils import BaseResponse

class MatchSchema(BaseModel):
    id: uuid.UUID
    question: str
    answer: str
    color: str

class MatchResponse(BaseResponse):
    data: list[MatchSchema]