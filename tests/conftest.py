import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db, SessionLocal
from app.models import Base
from app.auth import get_password_hash

@pytest.fixture
def client():
    init_db()
    db = SessionLocal()
    # Добавляем тестовых пользователей, если их нет
    from app.models import User
    if not db.query(User).filter(User.username == "admin").first():
        db.add(User(username="admin", hashed_password=get_password_hash("admin123"), role="admin"))
    if not db.query(User).filter(User.username == "user").first():
        db.add(User(username="user", hashed_password=get_password_hash("user123"), role="employee"))
    db.commit()
    db.close()
    return TestClient(app)

@pytest.fixture
def user_token(client):
    r = client.post("/api/login", json={"username": "user", "password": "user123"})
    return r.json()["token"]

@pytest.fixture
def admin_token(client):
    r = client.post("/api/login", json={"username": "admin", "password": "admin123"})
    return r.json()["token"]