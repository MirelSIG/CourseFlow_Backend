"""
Define las pruebas unitarias y de integración para el flujo de autenticación de usuarios.
Cubre escenarios de registro de usuarios, manejo de correos duplicados, inicio de sesión exitoso y fallido, y revocación de sesión.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.utils.enums import Role

client = TestClient(app)

def test_register_user():
    """
    Verifica el registro correcto de un nuevo usuario en la plataforma.
    """
    # Prueba el registro exitoso.
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
    """
    Verifica que el sistema impida el registro de múltiples usuarios con la misma dirección de correo electrónico.
    """
    # 1. Registra el primer usuario.
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "User 1",
            "email": "dup@example.com",
            "password": "password123"
        }
    )
    # 2. Intenta registrar otro usuario con el mismo correo electrónico.
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
    """
    Verifica el inicio de sesión exitoso con credenciales correctas y la recepción de la cookie HttpOnly.
    """
    # 1. Registra al usuario de prueba.
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Login User",
            "email": "login@example.com",
            "password": "testpassword"
        }
    )
    # 2. Inicia sesión.
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
    """
    Verifica que el inicio de sesión retorne HTTP 401 si las credenciales son incorrectas.
    """
    # 1. Registra al usuario de prueba.
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Login User",
            "email": "wrong@example.com",
            "password": "testpassword"
        }
    )
    # 2. Intenta iniciar sesión con una contraseña incorrecta.
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
    """
    Verifica el cierre de sesión, la revocación del token en la lista negra y la denegación de acceso posterior.
    """
    # 1. Registra e inicia sesión.
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
    
    # 2. Cierra la sesión.
    logout_res = client.post("/api/v1/auth/logout", cookies=cookies)
    assert logout_res.status_code == 200
    
    # 3. Intenta reutilizar la cookie revocada en la lista negra.
    protected_res = client.post("/api/v1/auth/logout", cookies=cookies)
    assert protected_res.status_code == 401
    assert protected_res.json()["detail"] == "Token has been revoked"
