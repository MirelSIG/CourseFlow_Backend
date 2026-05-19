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
    token = generate_token(10, Role.SUPERADMIN.value)
    return {"access_token": token}

@pytest.fixture
def admin_token():
    token = generate_token(20, Role.ADMIN.value)
    return {"access_token": token}

@pytest.fixture
def user_token():
    token = generate_token(30, Role.USER.value)
    return {"access_token": token}

def test_admin_crud_flow(superadmin_token, db):
    # 1. Crear un administrador nuevo
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

    # 2. Intentar crear duplicado (mismo email)
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

    # 3. Listar administradores (debe aparecer el que acabamos de crear)
    res_list = client.get("/api/admin/users", cookies=superadmin_token)
    assert res_list.status_code == 200
    ids = [a["id"] for a in res_list.json()]
    assert admin_id in ids
    # Debe excluir a los usuarios de otros roles
    for admin in res_list.json():
        assert admin["role"] == Role.ADMIN.value

    # 4. Actualizar administrador
    res_patch = client.patch(
        f"/api/admin/users/{admin_id}",
        json={"name": "Updated Admin Test"},
        cookies=superadmin_token
    )
    assert res_patch.status_code == 200
    assert res_patch.json()["name"] == "Updated Admin Test"

    # 5. Eliminar administrador
    res_del = client.delete(f"/api/admin/users/{admin_id}", cookies=superadmin_token)
    assert res_del.status_code == 204

    # 6. Verificar que ya no exista
    res_get_del = client.get("/api/admin/users", cookies=superadmin_token)
    ids_del = [a["id"] for a in res_get_del.json()]
    assert admin_id not in ids_del

def test_admin_crud_unauthorized(user_token, admin_token):
    # Intentar crear con rol 'user'
    res_user = client.post(
        "/api/admin/users",
        json={"name": "No Access", "email": "no@courseflow.com", "password": "pass"},
        cookies=user_token
    )
    assert res_user.status_code == 403
    assert res_user.json()["detail"] == "Insufficient permissions"

    # Intentar crear con rol 'admin' (solo el superadmin puede gestionar admins)
    res_admin = client.post(
        "/api/admin/users",
        json={"name": "No Access", "email": "no@courseflow.com", "password": "pass"},
        cookies=admin_token
    )
    assert res_admin.status_code == 403
    assert res_admin.json()["detail"] == "Insufficient permissions"

def test_superadmin_prevent_self_deletion(superadmin_token):
    # Generar token para superadmin con ID 999
    token = generate_token(999, Role.SUPERADMIN.value)
    cookies = {"access_token": token}
    
    # Intentar eliminar a sí mismo (user_id = 999)
    res = client.delete("/api/admin/users/999", cookies=cookies)
    assert res.status_code == 400
    assert res.json()["detail"] == "El superadmin no puede eliminarse a sí mismo"
