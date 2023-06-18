from pydantic import BaseModel

import uuid

from utils import BaseResponse

class WorkspaceSchema(BaseModel):
    id: uuid.UUID
    title: str
    initial: bool

class NewWorkspaceSchema(BaseModel):
    id: uuid.UUID
    title: str

class WorkspaceResponse(BaseResponse):
    data: list[WorkspaceSchema]