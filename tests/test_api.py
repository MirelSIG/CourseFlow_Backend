from fastapi.testclient import TestClient

def test_user_registration_and_login(client: TestClient):
    # Register user
    user_data = {
        "email": "test@example.com",
        "password": "password123",
        "name": "Test User",
        "role": "user"
    }
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201, f"User registration failed: {response.json()}"

    # Login (tu API usa JSON, no form-data)
    login_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200, f"Login failed: {response.json()}"
    token = response.json()["access_token"]
    assert token


def test_course_and_application_flow(client: TestClient):
    # Register admin
    user_data = {
        "email": "admin_test@example.com",
        "password": "password123",
        "name": "Admin Test User",
        "role": "admin"
    }
    client.post("/api/v1/auth/register", json=user_data)

    # Login
    login_data = {
        "email": "admin_test@example.com",
        "password": "password123"
    }
    login_response = client.post("/api/v1/auth/login", json=login_data)
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create course
    course_data = {
        "name": "Python Advanced",
        "description": "Advanced Python course",
        "start_date": "2026-06-01",
        "end_date": "2026-07-01",
        "capacity": 30,
        "is_active": True
    }
    response = client.post("/api/v1/courses/", json=course_data, headers=headers)
    assert response.status_code == 201, f"Course creation failed: {response.json()}"
    course_id = response.json()["id"]

    # List
