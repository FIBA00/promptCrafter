import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import app
from db.database import get_db, Base
from core.config import settings

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
