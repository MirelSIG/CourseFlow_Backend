import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.utils.enums import Role

client = TestClient(app)

def test_register_user():
    # Test successful registration
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "testpassword",
            "role": Role.USER.value
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"

def test_register_duplicate_email():
    # 1. Register first user
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "User 1",
            "email": "dup@example.com",
            "password": "password123"
        }
    )
    # 2. Try to register again with same email
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "User 2",
            "email": "dup@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "Email already registered"

def test_login_success():
    # 1. Register user
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Login User",
            "email": "login@example.com",
            "password": "testpassword"
        }
    )
    # 2. Login
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "login@example.com",
            "password": "testpassword"
        }
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Logged in successfully"
    assert "access_token" in response.cookies

def test_login_invalid_credentials():
    # 1. Register user
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Login User",
            "email": "wrong@example.com",
            "password": "testpassword"
        }
    )
    # 2. Login with wrong password
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "wrong@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

def test_logout():
    # 1. Register and Login
    email = "logout@example.com"
    pwd = "password123"
    client.post(
        "/api/v1/auth/register",
        json={"name": "U", "email": email, "password": pwd}
    )
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": pwd}
    )
    cookies = login_res.cookies
    
    # 2. Logout
    logout_res = client.post("/api/v1/auth/logout", cookies=cookies)
    assert logout_res.status_code == 200
    
    # 3. Try to use blacklisted cookie
    protected_res = client.post("/api/v1/auth/logout", cookies=cookies)
    assert protected_res.status_code == 401
    assert protected_res.json()["detail"] == "Token has been revoked"
