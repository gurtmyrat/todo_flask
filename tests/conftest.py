import pytest
from flask_jwt_extended import create_access_token
from api import create_app
from api.models.base import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

TEST_DATABASE_URL = os.getenv('DATABASE_URL')

@pytest.fixture(scope="session", autouse=True)
def app_dict():
    print(TEST_DATABASE_URL)
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": TEST_DATABASE_URL,
        "SQLALCHEMY_TRACK_MODIFICATIONS": False
    })

    engine = create_engine(TEST_DATABASE_URL)
    Session = sessionmaker(bind=engine)

    with app.app_context():
        Base.metadata.create_all(engine)

        yield {"app": app, "db_session": Session()}

        Base.metadata.drop_all(engine)

@pytest.fixture
def client(app_dict):
    app = app_dict['app']
    db_session = app_dict['db_session']
    client = app.test_client()

    yield client

    db_session.rollback()

@pytest.fixture
def auth_header(client):
    access_token = create_access_token(identity=1)
    return {'Authorization': f'Bearer {access_token}'}
