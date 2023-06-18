from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import openai

from config import sqlalchemy_url, OPENAI_API_KEY

sqlalchemy_session = sessionmaker(create_engine(sqlalchemy_url))

openai.api_key = OPENAI_API_KEY