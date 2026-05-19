import pytest
from fastapi.testclient import TestClient
from app.models.user import User
from app.utils.enums import Role
from app.core.security import hash_password
from tests.test_auth_middleware import generate_token

def test_get_me_unauthorized(client: TestClient):
    res = client.get("/api/v1/users/me")
    assert res.status_code == 401

def test_get_me_success(client: TestClient, db):
    user = User(
        name="Profile Tester",
        email="profile@example.com",
        password=hash_password("password123"),
        role=Role.USER.value
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = generate_token(user.id, Role.USER.value)
    res = client.get("/api/v1/users/me", cookies={"access_token": token})
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "Profile Tester"
    assert data["email"] == "profile@example.com"
    assert "password_hash" not in data

def test_patch_me_success(client: TestClient, db):
    user = User(
        name="Old Name",
        email="old@example.com",
        password=hash_password("password123"),
        role=Role.USER.value
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = generate_token(user.id, Role.USER.value)
    res = client.patch(
        "/api/v1/users/me",
        json={"name": "New Name", "email": "new@example.com", "dni_nie": "12345678Z"},
        cookies={"access_token": token}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "New Name"
    assert data["email"] == "new@example.com"
    assert data["dni_nie"] == "12345678Z"

def test_patch_me_email_conflict(client: TestClient, db):
    user1 = User(
        name="User One",
        email="user1@example.com",
        password=hash_password("password123"),
        role=Role.USER.value
    )
    user2 = User(
        name="User Two",
        email="user2@example.com",
        password=hash_password("password123"),
        role=Role.USER.value
    )
    db.add(user1)
    db.add(user2)
    db.commit()
    db.refresh(user1)
    db.refresh(user2)

    token = generate_token(user1.id, Role.USER.value)
    res = client.patch(
        "/api/v1/users/me",
        json={"email": "user2@example.com"},
        cookies={"access_token": token}
    )
    assert res.status_code == 400
    assert "Email already registered" in res.json()["detail"]

def test_superadmin_bootstrap(db, monkeypatch):
    from app.core.config import settings
    from app.main import on_startup
    
    monkeypatch.setattr(settings, "SQLALCHEMY_DATABASE_URI", "sqlite:///./test_courseflow.db")
    monkeypatch.setenv("SUPERADMIN_EMAIL", "superadmin_test_bootstrap@example.com")
    monkeypatch.setenv("SUPERADMIN_PASSWORD", "superpassword123")
    
    on_startup()
    
    superadmin = db.query(User).filter(User.email == "superadmin_test_bootstrap@example.com").first()
    assert superadmin is not None
    assert superadmin.role == Role.SUPERADMIN.value
