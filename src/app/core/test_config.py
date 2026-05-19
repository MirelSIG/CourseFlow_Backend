"""
Define las configuraciones específicas para el entorno de pruebas de CourseFlow.
Utiliza una base de datos SQLite en memoria para asegurar el aislamiento durante la ejecución de las pruebas.
"""

from pydantic_settings import BaseSettings

class TestSettings(BaseSettings):
    """
    Representa el contenedor de configuraciones utilizado exclusivamente en la ejecución de pruebas.
    """
    PROJECT_NAME: str = "CourseFlow API - Test Suite"
    
    # Emplea una base de datos SQLite en memoria por defecto para las pruebas.
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///:memory:"
    
    BACKEND_CORS_ORIGINS: list[str] = []
    
    # Emplea una clave secreta y algoritmo fijos para los tokens de prueba.
    JWT_SECRET_KEY: str = "TEST_SECRET_KEY"
    JWT_ALGORITHM: str = "HS256"

# Instancia el objeto global de configuraciones de prueba.
test_settings = TestSettings()
