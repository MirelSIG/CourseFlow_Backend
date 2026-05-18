import pytest
from app.api.deps import get_db

@pytest.fixture
def db_session():
    # Usa la misma sesión que FastAPI usa en los tests
    generator = get_db()
    db = next(generator)
    try:
        yield db
    finally:
        try:
            next(generator)
        except StopIteration:
            pass
