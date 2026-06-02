"""
Define las pruebas unitarias para el middleware de autorización y control de acceso basado en roles.
Verifica la expiración de tokens, validación de firmas, jerarquía de roles y manejo de accesos no autorizados.
"""

import pytest
import datetime
from fastapi import FastAPI, Depends, Request
from fastapi.testclient import TestClient
from jose import jwt

from app.utils.decorators import require_auth, require_role, SECRET_KEY, ALGORITHM
from app.utils.enums import Role
from app.api.deps import get_db

app = FastAPI()

@pytest.fixture(autouse=True)
def override_middleware_db(db):
    """
    Sobrescribe la dependencia get_db de FastAPI local de middleware para usar la BD de tests.
    """
    app.dependency_overrides[get_db] = lambda: db
    yield
    del app.dependency_overrides[get_db]


@app.get("/protected")
def protected_route(user=Depends(require_auth)):
    return {"message": "success"}

@app.get("/admin_only")
def admin_only_route(user=Depends(require_role([Role.ADMIN]))):
    return {"message": "admin success"}

@app.get("/superadmin_only")
def superadmin_only_route(user=Depends(require_role([Role.SUPERADMIN]))):
    return {"message": "superadmin success"}

client = TestClient(app)

def generate_token(user_id, role, exp_offset=3600):
    """
    Genera un token JWT de prueba firmado con una clave secreta temporal.
    """
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=exp_offset)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def test_require_auth_missing_cookie():
    """
    Verifica que se retorne HTTP 401 si no se proporciona la cookie de autenticación.
    """
    res = client.get("/protected")
    assert res.status_code == 401
    assert "Missing authentication cookie" in res.json()["detail"]

def test_require_auth_invalid_token():
    """
    Verifica que se retorne HTTP 401 ante una firma o estructura de token incorrecta.
    """
    # Envia una cookie con un valor inválido.
    res = client.get("/protected", cookies={"access_token": "invalid-token"})
    assert res.status_code == 401
    assert "Invalid token" in res.json()["detail"]

def test_require_auth_expired_token():
    """
    Verifica que se retorne HTTP 401 ante un token cuya vigencia ha expirado.
    """
    token = generate_token(1, Role.USER.value, exp_offset=-3600)
    res = client.get("/protected", cookies={"access_token": token})
    assert res.status_code == 401
    assert "Token has expired" in res.json()["detail"]

def test_require_auth_success():
    """
    Verifica el acceso exitoso a una ruta protegida con un token válido.
    """
    token = generate_token(1, Role.USER.value)
    res = client.get("/protected", cookies={"access_token": token})
    assert res.status_code == 200
    assert res.json()["message"] == "success"

def test_require_role_user_in_admin_route():
    """
    Verifica que un usuario estándar no pueda acceder a una ruta reservada para administradores.
    """
    token = generate_token(1, Role.USER.value)
    res = client.get("/admin_only", cookies={"access_token": token})
    assert res.status_code == 403
    assert res.json()["detail"] == "Insufficient permissions"

def test_require_role_admin_in_superadmin_route():
    """
    Verifica que un administrador estándar no pueda acceder a una ruta reservada para superadministradores.
    """
    token = generate_token(1, Role.ADMIN.value)
    res = client.get("/superadmin_only", cookies={"access_token": token})
    assert res.status_code == 403
    assert res.json()["detail"] == "Insufficient permissions"

def test_require_role_superadmin_in_admin_route():
    """
    Verifica que un superadministrador pueda acceder a rutas de administración debido a la jerarquía de roles.
    """
    token = generate_token(1, Role.SUPERADMIN.value)
    res = client.get("/admin_only", cookies={"access_token": token})
    assert res.status_code == 200
    assert res.json()["message"] == "admin success"
