from fastapi.testclient import TestClient
from app.main import app

from app.utils.enums import Role
from tests.test_auth_middleware import generate_token

client = TestClient(app)

def test_health():
    response = client.get("/docs")
    assert response.status_code == 200

def test_health_courses(client: TestClient):
    token = generate_token(1, Role.USER.value)
    response = client.get("/api/v1/courses/", cookies={"access_token": token})
    assert response.status_code == 200
