"""
Define las pruebas unitarias y de integración para la administración y gestión de administradores.
Cubre operaciones de creación, listado, actualización, eliminación de administradores y restricción de autoeliminación.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.utils.enums import Role
from app.models.user import User
from app.core.config import settings
from tests.test_auth_middleware import generate_token

client = TestClient(app)

@pytest.fixture
def superadmin_token():
    """
    Fixture auxiliar que proporciona las cookies con token de superadministrador.
    """
    token = generate_token(10, Role.SUPERADMIN.value)
    return {"access_token": token}

@pytest.fixture
def admin_token():
    """
    Fixture auxiliar que proporciona las cookies con token de administrador estándar.
    """
    token = generate_token(20, Role.ADMIN.value)
    return {"access_token": token}

@pytest.fixture
def user_token():
    """
    Fixture auxiliar que proporciona las cookies con token de usuario estándar.
    """
    token = generate_token(30, Role.USER.value)
    return {"access_token": token}

def test_admin_crud_flow(superadmin_token, db):
    """
    Verifica el flujo CRUD completo (creación, duplicado, listado, actualización y eliminación) realizado por el superadministrador.
    """
    # 1. Crea un administrador nuevo.
    res = client.post(
        "/api/admin/users",
        json={
            "name": "New Admin Test",
            "email": "newadmin@courseflow.com",
            "password": "securepassword"
        },
        cookies=superadmin_token
    )
    assert res.status_code == 201
    assert res.json()["name"] == "New Admin Test"
    assert res.json()["role"] == Role.ADMIN.value
    admin_id = res.json()["id"]

    # 2. Intenta crear un administrador duplicado con el mismo correo electrónico.
    res_dup = client.post(
        "/api/admin/users",
        json={
            "name": "New Admin Dup",
            "email": "newadmin@courseflow.com",
            "password": "securepassword"
        },
        cookies=superadmin_token
    )
    assert res_dup.status_code == 400
    assert "Email already registered" in res_dup.json()["detail"]

    # 3. Lista los administradores. Debe aparecer el que se acaba de crear.
    res_list = client.get("/api/admin/users", cookies=superadmin_token)
    assert res_list.status_code == 200
    ids = [a["id"] for a in res_list.json()]
    assert admin_id in ids
    # Excluye a los usuarios que no tengan el rol de administrador.
    for admin in res_list.json():
        assert admin["role"] == Role.ADMIN.value

    # 4. Actualiza la información del administrador.
    res_patch = client.patch(
        f"/api/admin/users/{admin_id}",
        json={"name": "Updated Admin Test"},
        cookies=superadmin_token
    )
    assert res_patch.status_code == 200
    assert res_patch.json()["name"] == "Updated Admin Test"

    # 5. Elimina al administrador.
    res_del = client.delete(f"/api/admin/users/{admin_id}", cookies=superadmin_token)
    assert res_del.status_code == 204

    # 6. Verifica que ya no aparezca en la lista de administradores.
    res_get_del = client.get("/api/admin/users", cookies=superadmin_token)
    ids_del = [a["id"] for a in res_get_del.json()]
    assert admin_id not in ids_del

def test_admin_crud_unauthorized(user_token, admin_token):
    """
    Verifica que usuarios y administradores estándar no tengan permisos para acceder a las rutas de administración.
    """
    # Intenta realizar la creación con el rol 'user'.
    res_user = client.post(
        "/api/admin/users",
        json={"name": "No Access", "email": "no@courseflow.com", "password": "pass"},
        cookies=user_token
    )
    assert res_user.status_code == 403
    assert res_user.json()["detail"] == "Insufficient permissions"

    # Intenta realizar la creación con el rol 'admin' (solo el superadmin puede gestionar admins).
    res_admin = client.post(
        "/api/admin/users",
        json={"name": "No Access", "email": "no@courseflow.com", "password": "pass"},
        cookies=admin_token
    )
    assert res_admin.status_code == 403
    assert res_admin.json()["detail"] == "Insufficient permissions"

def test_superadmin_prevent_self_deletion(superadmin_token):
    """
    Verifica que el superadministrador activo no pueda eliminarse a sí mismo de la base de datos.
    """
    # Genera un token para un superadmin ficticio con ID 999.
    token = generate_token(999, Role.SUPERADMIN.value)
    cookies = {"access_token": token}
    
    # Intenta realizar la eliminación del ID de sesión actual (999).
    res = client.delete("/api/admin/users/999", cookies=cookies)
    assert res.status_code == 400
    assert res.json()["detail"] == "El superadmin no puede eliminarse a sí mismo"
