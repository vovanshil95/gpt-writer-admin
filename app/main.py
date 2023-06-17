from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.responses import JSONResponse
from  sqlalchemy.exc import IntegrityError

from config import ORIGINS
from workspace.router import router as workspace_router
from gpt_interactions.router import router as interactions_router
from questions.router import router as questions_router
from prompts.router import router as prompts_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(workspace_router)
app.include_router(interactions_router)
app.include_router(questions_router)
app.include_router(prompts_router)

REQUEST_VALIDATION_ERROR_STATUS = 422
ENTITY_ERROR_STATUS = 400

@app.exception_handler(RequestValidationError)
def validation_handler(request, exc):
    return JSONResponse(status_code=ENTITY_ERROR_STATUS,
                        content={'status': 'error', 'message': exc.errors()[0]['msg']})


@app.exception_handler(IntegrityError)
def unique_vailation_handler(request, exc):
    if 'errors.UniqueViolation' in str(exc):
        return JSONResponse(status_code=ENTITY_ERROR_STATUS,
                            content={'status': 'error', 'message': 'Duplicate unique property detected'})
    else:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.exception_handler(AttributeError)
def entity_error_handler(request, exc):
    return JSONResponse(status_code=ENTITY_ERROR_STATUS, content={'status': 'error', 'message': str(exc)})
