"""
Contiene pruebas básicas de salud (health check) del sistema para asegurar
que la documentación de la API y los endpoints iniciales respondan correctamente.
"""

from fastapi.testclient import TestClient
from app.main import app

from app.utils.enums import Role
from tests.test_auth_middleware import generate_token

client = TestClient(app)

def test_health():
    """
    Verifica que el endpoint de la documentación de la API esté disponible y retorne HTTP 200.
    """
    response = client.get("/docs")
    assert response.status_code == 200

def test_health_courses(client: TestClient):
    """
    Verifica el acceso básico autenticado al listado de cursos para confirmar la conectividad del middleware.
    """
    token = generate_token(1, Role.USER.value)
    response = client.get("/api/v1/courses/", cookies={"access_token": token})
    assert response.status_code == 200
