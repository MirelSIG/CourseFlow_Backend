import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient
from app.models.user import User
from app.models.course import Course
from app.models.application import Application
from app.utils.enums import Role, ApplicationStatus
from app.core.security import hash_password
from tests.test_auth_middleware import generate_token

@pytest.fixture
def test_users(db):
    user = User(
        name="Student User",
        email="student@example.com",
        password=hash_password("password123"),
        role=Role.USER.value,
        dni_nie="12345678Z",
        birth_date=date(2000, 1, 1)
    )
    admin = User(
        name="Admin User",
        email="admin_app@example.com",
        password=hash_password("password123"),
        role=Role.ADMIN.value,
        dni_nie="87654321X",
        birth_date=date(1990, 5, 5)
    )
    other = User(
        name="Other Student",
        email="other@example.com",
        password=hash_password("password123"),
        role=Role.USER.value,
        dni_nie="12345677A",
        birth_date=date(1995, 10, 10)
    )
    db.add(user)
    db.add(admin)
    db.add(other)
    db.commit()
    db.refresh(user)
    db.refresh(admin)
    db.refresh(other)
    return {"user": user, "admin": admin, "other": other}

@pytest.fixture
def test_course(db):
    course = Course(
        name="FastAPI Testing",
        description="Learn FastAPI",
        start_date=date.today() + timedelta(days=10),
        end_date=date.today() + timedelta(days=20),
        capacity=2,
        is_active=True
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return course

def test_create_application_success(client: TestClient, db, test_users, test_course):
    token = generate_token(test_users["user"].id, Role.USER.value)
    res = client.post(
        "/api/v1/applications/",
        json={"course_id": test_course.id, "has_darde": True, "previous_education": "None"},
        cookies={"access_token": token}
    )
    assert res.status_code == 201
    assert res.json()["status"] == "pending"

def test_create_application_duplicate(client: TestClient, db, test_users, test_course):
    token = generate_token(test_users["user"].id, Role.USER.value)
    # First application
    client.post(
        "/api/v1/applications/",
        json={"course_id": test_course.id, "has_darde": True},
        cookies={"access_token": token}
    )
    # Second application (should be duplicate)
    res = client.post(
        "/api/v1/applications/",
        json={"course_id": test_course.id, "has_darde": True},
        cookies={"access_token": token}
    )
    assert res.status_code == 409
    assert "already applied" in res.json()["detail"]

def test_create_application_capacity_limit(client: TestClient, db, test_users, test_course):
    # Setup two accepted applications first
    app1 = Application(user_id=test_users["user"].id, course_id=test_course.id, status=ApplicationStatus.ACCEPTED, has_darde=True)
    app2 = Application(user_id=test_users["other"].id, course_id=test_course.id, status=ApplicationStatus.ACCEPTED, has_darde=True)
    db.add(app1)
    db.add(app2)
    db.commit()

    # Create a third user
    third_user = User(
        name="Third Student",
        email="third@example.com",
        password=hash_password("password123"),
        role=Role.USER.value,
        dni_nie="23456789W",
        birth_date=date(2001, 2, 2)
    )
    db.add(third_user)
    db.commit()
    db.refresh(third_user)

    token = generate_token(third_user.id, Role.USER.value)
    res = client.post(
        "/api/v1/applications/",
        json={"course_id": test_course.id, "has_darde": True},
        cookies={"access_token": token}
    )
    assert res.status_code == 400
    assert "Course is full" in res.json()["detail"]

def test_get_my_applications(client: TestClient, db, test_users, test_course):
    app = Application(user_id=test_users["user"].id, course_id=test_course.id, status=ApplicationStatus.PENDING, has_darde=True)
    db.add(app)
    db.commit()

    token = generate_token(test_users["user"].id, Role.USER.value)
    res = client.get("/api/v1/applications/me", cookies={"access_token": token})
    assert res.status_code == 200
    assert len(res.json()) == 1
    assert res.json()[0]["course_id"] == test_course.id

def test_update_application_status_admin(client: TestClient, db, test_users, test_course):
    app = Application(user_id=test_users["user"].id, course_id=test_course.id, status=ApplicationStatus.PENDING, has_darde=True)
    db.add(app)
    db.commit()
    db.refresh(app)

    token = generate_token(test_users["admin"].id, Role.ADMIN.value)
    res = client.patch(
        f"/api/v1/applications/{app.id}/status",
        json={"status": "accepted"},
        cookies={"access_token": token}
    )
    assert res.status_code == 200
    assert res.json()["status"] == "accepted"

def test_update_application_status_unauthorized(client: TestClient, db, test_users, test_course):
    app = Application(user_id=test_users["user"].id, course_id=test_course.id, status=ApplicationStatus.PENDING, has_darde=True)
    db.add(app)
    db.commit()
    db.refresh(app)

    token = generate_token(test_users["user"].id, Role.USER.value)
    res = client.patch(
        f"/api/v1/applications/{app.id}/status",
        json={"status": "accepted"},
        cookies={"access_token": token}
    )
    assert res.status_code == 403

def test_get_course_applications(client: TestClient, db, test_users, test_course):
    app = Application(user_id=test_users["user"].id, course_id=test_course.id, status=ApplicationStatus.PENDING, has_darde=True)
    db.add(app)
    db.commit()

    token = generate_token(test_users["admin"].id, Role.ADMIN.value)
    res = client.get(f"/api/v1/courses/{test_course.id}/applications", cookies={"access_token": token})
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert data[0]["user"]["name"] == "Student User"
    assert data[0]["user"]["email"] == "student@example.com"

def test_delete_application_user_cancel_own(client: TestClient, db, test_users, test_course):
    app = Application(user_id=test_users["user"].id, course_id=test_course.id, status=ApplicationStatus.PENDING, has_darde=True)
    db.add(app)
    db.commit()
    db.refresh(app)

    token = generate_token(test_users["user"].id, Role.USER.value)
    res = client.delete(f"/api/v1/applications/{app.id}", cookies={"access_token": token})
    assert res.status_code == 200
    assert res.json()["status"] == "cancelled"

def test_delete_application_user_cancel_other_forbidden(client: TestClient, db, test_users, test_course):
    app = Application(user_id=test_users["other"].id, course_id=test_course.id, status=ApplicationStatus.PENDING, has_darde=True)
    db.add(app)
    db.commit()
    db.refresh(app)

    token = generate_token(test_users["user"].id, Role.USER.value)
    res = client.delete(f"/api/v1/applications/{app.id}", cookies={"access_token": token})
    assert res.status_code == 403

def test_delete_application_admin_physical_delete(client: TestClient, db, test_users, test_course):
    app = Application(user_id=test_users["user"].id, course_id=test_course.id, status=ApplicationStatus.PENDING, has_darde=True)
    db.add(app)
    db.commit()
    db.refresh(app)

    token = generate_token(test_users["admin"].id, Role.ADMIN.value)
    res = client.delete(f"/api/v1/applications/{app.id}", cookies={"access_token": token})
    assert res.status_code == 204

    # Verify physical deletion
    assert db.get(Application, app.id) is None

def test_create_application_missing_dni(client: TestClient, db, test_course):
    # User with no DNI
    user = User(
        name="No DNI User",
        email="nodni@example.com",
        password=hash_password("password123"),
        role=Role.USER.value,
        birth_date=date(2000, 1, 1),
        dni_nie=None
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = generate_token(user.id, Role.USER.value)
    res = client.post(
        "/api/v1/applications/",
        json={"course_id": test_course.id, "has_darde": True},
        cookies={"access_token": token}
    )
    assert res.status_code == 400
    assert "DNI/NIE" in res.json()["detail"]

def test_create_application_invalid_dni_format(client: TestClient, db, test_course):
    # User with invalid DNI format (doesn't trigger schema because it's set directly in DB)
    user = User(
        name="Invalid DNI User",
        email="validdni@example.com",
        password=hash_password("password123"),
        role=Role.USER.value,
        birth_date=date(2000, 1, 1),
        dni_nie="12345Z"  # Invalid format
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = generate_token(user.id, Role.USER.value)
    res = client.post(
        "/api/v1/applications/",
        json={"course_id": test_course.id, "has_darde": True},
        cookies={"access_token": token}
    )
    assert res.status_code == 400
    assert "DNI/NIE" in res.json()["detail"]

def test_create_application_missing_birth_date(client: TestClient, db, test_course):
    # User with no birth date
    user = User(
        name="No Birth Date User",
        email="nobirth@example.com",
        password=hash_password("password123"),
        role=Role.USER.value,
        dni_nie="12345678Z",
        birth_date=None
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = generate_token(user.id, Role.USER.value)
    res = client.post(
        "/api/v1/applications/",
        json={"course_id": test_course.id, "has_darde": True},
        cookies={"access_token": token}
    )
    assert res.status_code == 400
    assert "birth date" in res.json()["detail"]

def test_create_application_underage(client: TestClient, db, test_course):
    # User who is under 18 years old
    user = User(
        name="Underage User",
        email="underage@example.com",
        password=hash_password("password123"),
        role=Role.USER.value,
        dni_nie="12345678Z",
        birth_date=date.today() - timedelta(days=17 * 365)  # 17 years old
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = generate_token(user.id, Role.USER.value)
    res = client.post(
        "/api/v1/applications/",
        json={"course_id": test_course.id, "has_darde": True},
        cookies={"access_token": token}
    )
    assert res.status_code == 400
    assert "at least 18 years old" in res.json()["detail"]
