import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.api.deps import get_db
from app.main import app
from fastapi.testclient import TestClient

# Usar una base de datos SQLite específica para pruebas
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_courseflow.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """
    Crea todas las tablas antes de ejecutar la suite de tests
    y las elimina al finalizar.
    """
    # Importar todos los modelos para asegurar que Base los conozca
    from app.models.user import User
    from app.models.course import Course
    from app.models.application import Application
    from app.models.waiting_list import WaitingList
    from app.models.token_blacklist import TokenBlacklist
    
    Base.metadata.create_all(bind=engine)
    yield
    # Opcional: Eliminar el archivo de base de datos de prueba al final
    if os.path.exists("./test_courseflow.db"):
        os.remove("./test_courseflow.db")

@pytest.fixture
def db():
    """
    Proporciona una sesión de base de datos limpia para cada test.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(autouse=True)
def override_get_db(db):
    """
    Sobrescribe la dependencia get_db de FastAPI para usar la BD de tests.
    """
    def _get_test_db():
        yield db
    app.dependency_overrides[get_db] = _get_test_db
    yield
    del app.dependency_overrides[get_db]

@pytest.fixture
def client():
    return TestClient(app)
