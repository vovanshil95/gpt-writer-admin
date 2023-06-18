from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from  sqlalchemy.exc import IntegrityError

from config import ORIGINS
from workspace.router import router as workspace_router
from gpt_interactions.router import router as interactions_router
from questions.router import router as questions_router
from prompts.router import router as prompts_router
from exception_handlers import validation_handler, unique_vailation_handler, entity_error_handler

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
app.add_exception_handler(RequestValidationError, validation_handler)
app.add_exception_handler(IntegrityError, unique_vailation_handler)
app.add_exception_handler(AttributeError, entity_error_handler)
