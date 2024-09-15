import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

@lru_cache(maxsize=None)
def _get_engine():
    engine = create_engine(os.getenv("DATABASE_URL"), echo=True)
    return engine

def get_session():
    engine = _get_engine()
    Session = sessionmaker(bind=engine)
    return Session()
