from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "CourseFlow API"
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///courseflow.db"
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    JWT_SECRET_KEY: str = "CHANGE_ME"
    JWT_ALGORITHM: str = "HS256"
    
    # Optional: override via environment variable for production
    DATABASE_URL_PROD: Optional[str] = None

    class Config:
        env_file = ".env"
    
    def __init__(self, **data):
        super().__init__(**data)
        # Allow override from environment variable for PostgreSQL
        if self.DATABASE_URL_PROD:
            self.SQLALCHEMY_DATABASE_URI = self.DATABASE_URL_PROD

settings = Settings()
