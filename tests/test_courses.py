import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.utils.enums import Role
from tests.test_auth_middleware import generate_token

client = TestClient(app)

@pytest.fixture
def user_token():
    # Helper para obtener cookies con token de user
    token = generate_token(1, Role.USER.value)
    return {"access_token": token}

@pytest.fixture
def admin_token():
    # Helper para obtener cookies con token de admin
    token = generate_token(2, Role.ADMIN.value)
    return {"access_token": token}

def test_create_course_success(admin_token):
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
    res = client.post(
        "/api/v1/courses/",
        json={
            "name": "Invalid Course",
            "description": "Desc",
            "start_date": "2026-02-01",
            "end_date": "2026-01-01", # End before start
            "capacity": 30
        },
        cookies=admin_token
    )
    assert res.status_code == 422
    assert res.json()["detail"] == "end_date must be strictly after start_date"

def test_create_course_unauthorized(user_token):
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
    res = client.put(
        "/api/v1/courses/1",
        json={"capacity": 50},
        cookies=user_token
    )
    assert res.status_code == 403

def test_delete_course_logical(admin_token, user_token):
    # 1. Create course
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

    # 2. Delete as admin
    res_delete = client.delete(f"/api/v1/courses/{course_id}", cookies=admin_token)
    assert res_delete.status_code == 204

    # 3. Verify it's logically deleted (is_active = False)
    # Admin should see it
    res_admin_get = client.get(f"/api/v1/courses/{course_id}", cookies=admin_token)
    assert res_admin_get.status_code == 200
    assert res_admin_get.json()["is_active"] is False

    # User should NOT see it
    res_user_get = client.get(f"/api/v1/courses/{course_id}", cookies=user_token)
    assert res_user_get.status_code == 404

def test_list_courses_filters(admin_token, user_token):
    # Crear un curso activo y uno inactivo
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
    
    # 1. List as user -> Should not see inactive
    user_list = client.get("/api/v1/courses/", cookies=user_token)
    assert user_list.status_code == 200
    names = [c["name"] for c in user_list.json()]
    assert "Active Course" in names
    assert "Inactive Course" not in names

    # 2. List as admin -> Should see both
    admin_list = client.get("/api/v1/courses/", cookies=admin_token)
    assert admin_list.status_code == 200
    names_admin = [c["name"] for c in admin_list.json()]
    assert "Active Course" in names_admin
    assert "Inactive Course" in names_admin
