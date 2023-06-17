from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import uuid

from utils import BaseResponse
from config import sqlalchemy_url
from models.models import Workspace, Match

router = APIRouter(prefix='/api/questions',
                   tags=['Questions'])

sqlalchemy_session = sessionmaker(create_engine(sqlalchemy_url))

class MatchSchema(BaseModel):
    id: uuid.UUID
    question: str
    answer: str
    color: str

class MatchResponse(BaseResponse):
    data: list[MatchSchema]

@router.get('')
def get_questions() -> MatchResponse:
    with sqlalchemy_session.begin() as session:
        matches = session.query(Match)\
            .filter(Match.workspace_id == session.query(Workspace.id).filter(Workspace.initial).first()[0])\
            .all()
        matches = list(map(lambda m: MatchSchema(id=str(m.id),
                                                 question=m.question,
                                                 answer=m.answer,
                                                 color=m.color), matches))
    return MatchResponse(status='success', message='Questions successfully retrieved', data=matches)

@router.put('')
def put_questions(questions: list[MatchSchema]) -> MatchResponse:
    with sqlalchemy_session.begin() as session:
        workspace_id = session.query(Workspace.id).filter(Workspace.initial).first()[0]
        session.query(Match)\
            .filter(Match.workspace_id == workspace_id)\
            .delete()
        session.add_all(map(lambda m: Match(m.id, m.question, m.answer, m.color, workspace_id), questions))
    return MatchResponse(status='success', message='Questions successfully saved', data=questions)