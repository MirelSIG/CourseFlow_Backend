import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db import session as db_session
from app.db.base import Base
from app.api.deps import get_db

# BD SQLite en memoria compartida
TEST_DATABASE_URL = "sqlite:///file::memory:?cache=shared"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False, "uri": True}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 1️⃣ Sobrescribir el engine y SessionLocal del proyecto
db_session.engine = engine
db_session.SessionLocal = TestingSessionLocal


# 2️⃣ Crear tablas antes de que FastAPI arranque
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# 3️⃣ Sobrescribir get_db para usar SQLite
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db


# 4️⃣ Desactivar startup/shutdown
app.router.on_startup = []
app.router.on_shutdown = []


# 5️⃣ Cliente de test
@pytest.fixture
def client():
    return TestClient(app)
