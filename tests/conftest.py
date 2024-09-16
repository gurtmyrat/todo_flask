import uuid
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.app import create_app
from api.models import Base, User
from flask_jwt_extended import create_access_token

@pytest.fixture(scope='session')
def app():
    app = create_app()
    return app

@pytest.fixture(scope='session')
def engine(app):
    return create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

@pytest.fixture(scope='session')
def connection(engine):
    connection = engine.connect()
    yield connection
    connection.close()

@pytest.fixture(scope='session')
def setup_db(connection):
    Base.metadata.create_all(connection)
    yield
    Base.metadata.drop_all(connection)

@pytest.fixture
def jwt_token(db_session):
    user = User(
        first_name='Test',
        last_name='User',
        username='testuser',
        email='testuser@example.com',
        password='password123'
    )
    db_session.add(user)
    db_session.commit()
    return create_access_token(identity=user.id)

@pytest.fixture(scope='function')
def db_session():
    app = create_app()
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

@pytest.fixture
def setup_test_user(db_session):
    unique_id = str(uuid.uuid4())
    user = User(
        first_name='John',
        last_name='Doe',
        username=f'johndoe_{unique_id}',
        email=f'johndoe_{unique_id}@example.com',
        password='password123'
    )
    user.password = "password123"
    db_session.add(user)
    db_session.commit()
    yield user
    db_session.query(User).filter_by(username=f'johndoe_{unique_id}').delete()
    db_session.commit()


@pytest.fixture
def setup_test_users(db_session):
    user1 = User(
        first_name="John10",
        last_name="Doe10",
        username="johndoe10",
        email="john10@example.com",
        password="password123"
    )
    user2 = User(
        first_name="Jane",
        last_name="Doe",
        username="janedoe",
        email="jane@example.com",
        password="password123"
    )
    user1.password = "password123"
    user2.password = "password123"

    db_session.add(user1)
    db_session.add(user2)
    db_session.commit()

    yield user1, user2

    db_session.delete(user1)
    db_session.delete(user2)
    db_session.commit()
