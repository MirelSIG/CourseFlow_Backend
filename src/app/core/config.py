"""
Define las configuraciones para la aplicación CourseFlow.
Carga variables de entorno desde un archivo .env y maneja configuraciones por defecto.
"""

from pydantic import Field, AliasChoices, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import os
import secrets

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
        ENVIRONMENT: str = "development"  # "development" | "production"
        FRONTEND_URL: str | None = None  # URL del frontend en producción (para CORS).

        SQLALCHEMY_DATABASE_URI: str | None = Field(
            default=None,
            validation_alias=AliasChoices("DATABASE_URL", "SQLALCHEMY_DATABASE_URI")
        )

        DB_HOST: str = "localhost"
        DB_PORT: int = 5432
        DB_USER: str = "courseflow"
        DB_PASSWORD: str = "courseflow"
        DB_NAME: str = "courseflow"

        BACKEND_CORS_ORIGINS: str | list[str] = ["http://localhost:5173", "http://localhost:3000"]

        JWT_SECRET_KEY: str = Field(
            default="CHANGE_ME",
            validation_alias=AliasChoices("JWT_SECRET_KEY", "SECRET_KEY")
        )
        JWT_ALGORITHM: str = "HS256"
        ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

        @model_validator(mode="after")
        def validate_production_secrets(self):
            """Impide arrancar en producción con secretos inseguros o de prueba."""
            insecure_values = {"CHANGE_ME", "your-jwt-secret-key-here", "secret", ""}
            if self.ENVIRONMENT == "production" and self.JWT_SECRET_KEY in insecure_values:
                raise ValueError(
                    "JWT_SECRET_KEY no es seguro para producción. "
                    "Genera uno con: python -c \"import secrets; print(secrets.token_hex(32))\""
                )
            return self

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
