"""
Define las pruebas unitarias y de integración para la gestión de cursos.
Verifica la creación de cursos, validaciones de fechas, control de accesos y la eliminación lógica.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.utils.enums import Role
from tests.test_auth_middleware import generate_token

client = TestClient(app)

@pytest.fixture
def user_token():
    """
    Fixture auxiliar que proporciona las cookies correspondientes a una sesión de usuario estándar.
    """
    token = generate_token(1, Role.USER.value)
    return {"access_token": token}

@pytest.fixture
def admin_token():
    """
    Fixture auxiliar que proporciona las cookies correspondientes a una sesión de administrador.
    """
    token = generate_token(2, Role.ADMIN.value)
    return {"access_token": token}

def test_create_course_success(admin_token):
    """
    Verifica que un administrador pueda crear un curso proporcionando datos y fechas válidas.
    """
    res = client.post(
        "/api/v1/courses/",
        json={
            "name": "Valid Course",
            "description": "Desc",
            "start_date": "2026-01-01",
            "end_date": "2026-02-01",
            "capacity": 30
        },
        cookies=admin_token
    )
    assert res.status_code == 201
    assert res.json()["name"] == "Valid Course"

def test_create_course_invalid_dates(admin_token):
    """
    Verifica que el endpoint retorne HTTP 422 si la fecha de fin es anterior o igual a la de inicio.
    """
    res = client.post(
        "/api/v1/courses/",
        json={
            "name": "Invalid Course",
            "description": "Desc",
            "start_date": "2026-02-01",
            "end_date": "2026-01-01", # Fin antes de inicio
            "capacity": 30
        },
        cookies=admin_token
    )
    assert res.status_code == 422
    assert res.json()["detail"] == "end_date must be strictly after start_date"

def test_create_course_unauthorized(user_token):
    """
    Verifica que un usuario sin privilegios de administrador no pueda crear cursos.
    """
    res = client.post(
        "/api/v1/courses/",
        json={
            "name": "Unauthorized Course",
            "start_date": "2026-01-01",
            "end_date": "2026-02-01"
        },
        cookies=user_token
    )
    assert res.status_code == 403

def test_update_course_unauthorized(user_token):
    """
    Verifica que un usuario sin privilegios de administrador no pueda actualizar un curso.
    """
    res = client.put(
        "/api/v1/courses/1",
        json={"capacity": 50},
        cookies=user_token
    )
    assert res.status_code == 403

def test_delete_course_logical(admin_token, user_token):
    """
    Verifica que la eliminación de un curso sea una baja lógica, haciéndolo invisible para usuarios pero visible para administradores.
    """
    # 1. Crea el curso de prueba.
    res_create = client.post(
        "/api/v1/courses/",
        json={
            "name": "Course to delete",
            "start_date": "2026-01-01",
            "end_date": "2026-02-01"
        },
        cookies=admin_token
    )
    course_id = res_create.json()["id"]

    # 2. Realiza la eliminación como administrador.
    res_delete = client.delete(f"/api/v1/courses/{course_id}", cookies=admin_token)
    assert res_delete.status_code == 204

    # 3. Verifica que se ha realizado la baja lógica (is_active = False).
    # Un administrador debe poder seguir viéndolo.
    res_admin_get = client.get(f"/api/v1/courses/{course_id}", cookies=admin_token)
    assert res_admin_get.status_code == 200
    assert res_admin_get.json()["is_active"] is False

    # Un usuario estándar no debe poder acceder al curso.
    res_user_get = client.get(f"/api/v1/courses/{course_id}", cookies=user_token)
    assert res_user_get.status_code == 404

def test_list_courses_filters(admin_token, user_token):
    """
    Verifica que los usuarios estándar no visualicen cursos inactivos en el listado, mientras que los administradores sí.
    """
    # Crea un curso activo y uno inactivo para verificar el filtrado.
    client.post(
        "/api/v1/courses/",
        json={"name": "Active Course", "start_date": "2026-01-01", "end_date": "2026-02-01", "is_active": True},
        cookies=admin_token
    )
    
    inactive_res = client.post(
        "/api/v1/courses/",
        json={"name": "Inactive Course", "start_date": "2026-01-01", "end_date": "2026-02-01", "is_active": False},
        cookies=admin_token
    )
    
    # 1. Recupera el listado como usuario estándar. No debe incluir el curso inactivo.
    user_list = client.get("/api/v1/courses/", cookies=user_token)
    assert user_list.status_code == 200
    names = [c["name"] for c in user_list.json()]
    assert "Active Course" in names
    assert "Inactive Course" not in names

    # 2. Recupera el listado como administrador. Debe incluir ambos cursos.
    admin_list = client.get("/api/v1/courses/", cookies=admin_token)
    assert admin_list.status_code == 200
    names_admin = [c["name"] for c in admin_list.json()]
    assert "Active Course" in names_admin
    assert "Inactive Course" in names_admin
