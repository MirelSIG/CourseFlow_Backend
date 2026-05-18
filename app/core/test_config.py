from pydantic_settings import BaseSettings

class TestSettings(BaseSettings):
    PROJECT_NAME: str = "CourseFlow API - Test"
    SQLALCHEMY_DATABASE_URI: str = "postgresql://user:password@localhost:5432/courseflow_test_db"
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    JWT_SECRET_KEY: str = "TEST_SECRET"
    JWT_ALGORITHM: str = "HS256"

test_settings = TestSettings()
