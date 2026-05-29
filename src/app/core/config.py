"""
Define las configuraciones para la aplicación CourseFlow.
Carga variables de entorno desde un archivo .env y maneja configuraciones por defecto.
"""

from pydantic import Field, AliasChoices, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import os

# Redirecciona a la configuración de pruebas si la variable de entorno TESTING está activa.
if os.getenv("TESTING"):
    from .test_config import test_settings as settings
else:
    class Settings(BaseSettings):
        """
        Representa la configuración central de la aplicación cargada desde variables de entorno.
        """
        model_config = SettingsConfigDict(
            env_file=".env",
            extra="ignore"
        )

        PROJECT_NAME: str = "CourseFlow API"

        SQLALCHEMY_DATABASE_URI: str | None = Field(
            default=None,
            validation_alias=AliasChoices("DATABASE_URL", "SQLALCHEMY_DATABASE_URI")
        )

        DB_HOST: str = "localhost"
        DB_PORT: int = 5432
        DB_USER: str = "courseflow"
        DB_PASSWORD: str = "courseflow"
        DB_NAME: str = "courseflow"

        BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

        JWT_SECRET_KEY: str = "CHANGE_ME"
        JWT_ALGORITHM: str = "HS256"
        ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

        @model_validator(mode="after")
        def assemble_db_uri(self):
            if not self.SQLALCHEMY_DATABASE_URI:
                self.SQLALCHEMY_DATABASE_URI = (
                    f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@"
                    f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
                )
            return self

    # Instancia el objeto global de configuraciones.
    settings = Settings()
