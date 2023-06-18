from pydantic import BaseModel

import uuid
import datetime

from utils import BaseResponse

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
