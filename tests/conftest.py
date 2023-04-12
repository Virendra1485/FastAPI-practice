from passlib.hash import bcrypt
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import app
from database import get_db
import models
from fastapi.testclient import TestClient
from item_route import create_access_token


@pytest.fixture(scope="function")
def db():
    engine = create_engine("postgresql://postgres:Test#123@localhost:5432/myapp_test")
    models.Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    # models.Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            db.rollback()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="function", autouse=True)
def drop_db_after_tests(db):
    yield
    models.Base.metadata.drop_all(db.bind)


@pytest.fixture(scope="function")
def create_test_user(db):
    user = models.User({"email": "test@gmail.com", "password": bcrypt.hash("Test@123")})
    db.add(user)
    db.commit()
    return user


@pytest.fixture(scope="function")
def get_auth_token():
    access_token = create_access_token({"sub": "test@gmail.com"})
    return {"Authorization": f"Bearer {access_token.decode('utf-8')}"}
