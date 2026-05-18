from fastapi.testclient import TestClient
from app.main import app
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.user import User
from app.models.token_blacklist import TokenBlacklist

client = TestClient(app)


def setup_user():
    db = SessionLocal()
    user = User(
        name="Test User",
        email="test@example.com",
        password_hash=hash_password("123456"),
        role="user"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user


def test_register_duplicate_email():
    setup_user()
    response = client.post("/api/v1/auth/register", json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "123456",
        "role": "user"
    })
    assert response.status_code == 409


def test_login_wrong_password():
    setup_user()
    response = client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "wrongpass"
    })
    assert response.status_code == 401


def test_revoked_token_cannot_be_used():
    setup_user()

    # login
    login = client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "123456"
    })
    token = login.json()["access_token"]

    # logout → blacklist
    client.post("/api/v1/auth/logout", headers={"Authorization": f"Bearer {token}"})

    # intentar usar token revocado
    response = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
