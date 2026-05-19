from pydantic_settings import BaseSettings, SettingsConfigDict
import os

if os.getenv("TESTING"):
    from .test_config import test_settings as settings
else:
    class Settings(BaseSettings):
        model_config = SettingsConfigDict(
            env_file=".env", 
            extra="ignore"
        )

        PROJECT_NAME: str = "CourseFlow API"
        SQLALCHEMY_DATABASE_URI: str = "sqlite:///./courseflow.db"
        BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]
        JWT_SECRET_KEY: str = "CHANGE_ME"
        JWT_ALGORITHM: str = "HS256"

    settings = Settings()
