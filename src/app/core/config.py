from pydantic import Field, AliasChoices
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
        SQLALCHEMY_DATABASE_URI: str = Field(
            default="sqlite:///./courseflow.db",
            validation_alias=AliasChoices("DATABASE_URL", "SQLALCHEMY_DATABASE_URI")
        )
        BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]
        JWT_SECRET_KEY: str = "CHANGE_ME"
        JWT_ALGORITHM: str = "HS256"

    settings = Settings()
