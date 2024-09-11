from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from functools import lru_cache
from api.config import settings

Base = declarative_base()

@lru_cache(maxsize=None)
def _get_engine():
    engine = create_engine(settings.DATABASE_URL, echo=True)
    return engine

def get_session():
    engine = _get_engine()
    Session = sessionmaker(bind=engine)
    return Session()
