import sys
from unittest.mock import MagicMock

# Mock sqladmin to avoid install requirement for tests
sys.modules["sqladmin"] = MagicMock()
sys.modules["sqladmin.authentication"] = MagicMock()
sys.modules["prometheus_fastapi_instrumentator"] = MagicMock()
sys.modules["fastapi_cache"] = MagicMock()
sys.modules["fastapi_cache.backends.redis"] = MagicMock()
sys.modules["redis"] = MagicMock()
sys.modules["redis.asyncio"] = MagicMock()

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import uuid

import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import app
from db.database import get_db, Base
from db.models import User
from core.config import settings
from core.oauth2 import create_access_token, hash_password

# 1. Setup Test Database URL
# We replace the DB name in the connection string to point to our test DB
TEST_DATABASE_URL = f"postgresql://{settings.DATABASE_USERNAME}:{settings.DATABASE_PASSWORD}@{settings.DATABASE_HOSTNAME}:{settings.DATABASE_PORT}/promptcrafter_test_db"

# 2. Create Test Engine
engine = create_engine(TEST_DATABASE_URL)

# 3. Create Test SessionLocal
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def setup_database():
    """
    Create tables at start of testing session, drop them at the end.
    """
    # Create all tables
    Base.metadata.create_all(bind=engine)
    yield
    # Drop all tables
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(setup_database):
    """
    Creates a new database session for a test.
    Rolls back changes after the test so tests are isolated.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    """
    FastAPI TestClient that overrides the get_db dependency
    to use our test database session.
    """

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(db_session):
    """
    Creates a verified test user and returns the user object.
    """
    password = "testpassword"
    hashed_pwd = hash_password(password)
    user = User(
        user_id=str(uuid.uuid4()),
        username="testuser",
        email="testuser@example.com",
        password=hashed_pwd,
        is_verified=True,
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture(scope="function")
def test_user_token(test_user):
    """
    Returns a valid access token for the verified test user.
    """
    return create_access_token(
        {
            "user_id": test_user.user_id,
            "email": test_user.email,
            "is_verified": test_user.is_verified,
        }
    )


@pytest.fixture(scope="function")
def unverified_user(db_session):
    """
    Creates an unverified test user.
    """
    password = "testpassword"
    hashed_pwd = hash_password(password)
    user = User(
        user_id=str(uuid.uuid4()),
        username="unverified",
        email="unverified@example.com",
        password=hashed_pwd,
        is_verified=False,
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture(scope="function")
def unverified_user_token(unverified_user):
    """
    Returns a valid access token for the unverified test user.
    """
    return create_access_token(
        {
            "user_id": unverified_user.user_id,
            "email": unverified_user.email,
            "is_verified": unverified_user.is_verified,
        }
    )
