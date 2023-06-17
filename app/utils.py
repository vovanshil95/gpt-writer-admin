from pydantic import BaseModel

class BaseResponse(BaseModel):
    status: str
    message: str
    data: dict