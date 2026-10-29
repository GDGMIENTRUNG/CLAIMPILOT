import os
import uuid
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from app.database import Base, get_db
from app.main import app
from app.config import settings
from scripts.seed_data import seed

@pytest.fixture
def db():
    # Each test owns a random schema; never truncate application tables.
    engine = create_engine(os.getenv('TEST_DATABASE_URL', settings.database_url), pool_pre_ping=True)
    schema = 'test_' + uuid.uuid4().hex
    with engine.connect() as connection:
        connection.execute(text(f'CREATE SCHEMA "{schema}"'))
        connection.commit()
        connection.execute(text(f'SET search_path TO "{schema}"'))
        Base.metadata.create_all(connection)
        connection.commit()
        with Session(connection, expire_on_commit=False) as session:
            seed(session)
            yield session
        connection.rollback()
        connection.execute(text('SET search_path TO public'))
        connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        connection.commit()
    engine.dispose()

@pytest.fixture
def client(db):
    def override():
        yield db
    app.dependency_overrides[get_db] = override
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
