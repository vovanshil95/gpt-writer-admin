from fastapi import APIRouter

from workspace.models import Workspace
from questions.models import Match
from init import sqlalchemy_session
from questions.schemas import MatchSchema, MatchResponse

router = APIRouter(prefix='/api/questions',
                   tags=['Questions'])

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
        session.add_all(map(lambda m: Match(id=m.id,
                                            question=m.question,
                                            answer=m.answer,
                                            color=m.color,
                                            workspace_id=workspace_id),
                            questions))
    return MatchResponse(status='success', message='Questions successfully saved', data=questions)
