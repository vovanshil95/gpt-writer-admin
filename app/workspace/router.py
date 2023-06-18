from fastapi import APIRouter

import uuid

from workspace.models import Workspace
from init import  sqlalchemy_session
from workspace.schemas import WorkspaceSchema, WorkspaceResponse, NewWorkspaceSchema

router = APIRouter(prefix='/api/workspace',
                   tags=['Workspace'])

def get_workspace_list(message: str) -> WorkspaceResponse:
    with sqlalchemy_session.begin() as session:
        workspaces = list(map(lambda w: WorkspaceSchema(id=w.id,
                                                        title=w.title,
                                                        initial=w.initial), session.query(Workspace).all()))
    return WorkspaceResponse(status='success', message=message, data=workspaces)

@router.get('')
def get_workspace() -> WorkspaceResponse:
    return get_workspace_list('Workspaces successfully retrieved')

@router.post('')
def add_edit_workspace(workspace: NewWorkspaceSchema) -> WorkspaceResponse:
    with sqlalchemy_session.begin() as session:
        old_workspace = session.get(Workspace, workspace.id)
        if old_workspace is None:
            session.add(Workspace(id=workspace.id,
                                  title=workspace.title,
                                  initial=False))
        else:
            old_workspace.title = workspace.title
    return get_workspace_list(f'workspace successfully {"edited" if old_workspace else "added"}')

@router.put('')
def goto_workspace(id: uuid.UUID) -> WorkspaceResponse:
    with sqlalchemy_session.begin() as session:
        new_workspace = session.get(Workspace, id)
        if new_workspace is None: raise AttributeError("workspace doesn't exist")
        session.query(Workspace).filter(Workspace.initial).first().initial = False
        new_workspace.initial = True
    return get_workspace_list('Initial Workspace successfully changed')

@router.delete('')
def delete_workspace(id: uuid.UUID) -> WorkspaceResponse:
    with sqlalchemy_session.begin() as session:
        workspace = session.get(Workspace, id)
        if workspace is None: raise AttributeError("Id doesn't exist")
        if workspace.initial: raise AttributeError("Can't remove initial workspace")
        session.delete(workspace)
    return get_workspace_list('Workspaces successfully deleted')
