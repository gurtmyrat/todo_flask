import uuid
import pytest
import subprocess
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from api.app import create_app
from api.models import  User
from flask_jwt_extended import create_access_token
from sqlalchemy.exc import ProgrammingError

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
def setup_db(engine):
    subprocess.run(['alembic', 'upgrade', 'head'], check=True)
    yield
    subprocess.run(['alembic', 'downgrade', 'base'], check=True)


@pytest.fixture
def db_session(app, engine, setup_db):
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.rollback()
        session.close()

@pytest.fixture
def unique_email():
    return f"testuser_{uuid.uuid4()}@example.com"

@pytest.fixture
def unique_username():
    return f"testuser_{uuid.uuid4()}"

@pytest.fixture
def setup_test_user(db_session, unique_email, unique_username):
    user = User(
        first_name='John',
        last_name='Doe',
        username=unique_username,
        email=unique_email,
        password='password123'
    )
    user.password = "password123"
    db_session.add(user)
    db_session.commit()
    yield user
    db_session.query(User).filter_by(email=unique_email).delete(synchronize_session=False)
    db_session.commit()

@pytest.fixture
def setup_test_users(db_session, unique_email, unique_username):
    user1 = User(
        first_name="John10",
        last_name="Doe10",
        username=f"{unique_username}_1",
        email=f"john10_{uuid.uuid4()}@example.com",
        password="password123"
    )
    user2 = User(
        first_name="Jane",
        last_name="Doe",
        username=f"{unique_username}_2",
        email=f"jane_{uuid.uuid4()}@example.com",
        password="password123"
    )
    db_session.add(user1)
    db_session.add(user2)
    db_session.commit()

    yield user1, user2

    db_session.query(User).filter(User.email.in_([user1.email, user2.email])).delete(synchronize_session=False)
    db_session.commit()


@pytest.fixture
def jwt_token(db_session):
    unique_email = f"testuser_{uuid.uuid4()}@example.com"
    unique_username = f"testuser_{uuid.uuid4()}"

    user = User(
        first_name='Test',
        last_name='User',
        username=unique_username,
        email=unique_email,
        password='password123'
    )
    db_session.add(user)
    db_session.commit()

    token = create_access_token(identity=user.id)

    db_session.query(User).filter_by(email=unique_email).delete(synchronize_session=False)
    db_session.commit()

    return token

@pytest.fixture(scope='function')
def setup_fake_enum(db_session):
    try:
        db_session.execute(text("""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'taskstatus') THEN
                    CREATE TYPE taskstatus AS ENUM ('NEW', 'IN_PROGRESS', 'COMPLETED');
                END IF;
            END
            $$;
        """))
        db_session.commit()
    except ProgrammingError as e:
        pytest.fail(f"Failed to create fake enum: {e}")

    yield

    try:
        # Clean up the enum type if needed
        db_session.execute(text("DROP TYPE IF EXISTS taskstatus"))
        db_session.commit()
    except ProgrammingError as e:
        pytest.fail(f"Failed to drop fake enum: {e}")


