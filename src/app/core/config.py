"""
Define las configuraciones para la aplicación CourseFlow.
Carga variables de entorno desde un archivo .env y maneja configuraciones por defecto.
"""

from pydantic import Field, AliasChoices
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
        
        # Proporciona la URI para la conexión con la base de datos, usando SQLite por defecto.
        SQLALCHEMY_DATABASE_URI: str = Field(
            default="sqlite:///./courseflow.db",
            validation_alias=AliasChoices("DATABASE_URL", "SQLALCHEMY_DATABASE_URI")
        )
        
        # Define los orígenes permitidos por CORS para las peticiones al backend.
        BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]
        
        # Define la clave secreta y el algoritmo utilizados para codificar y decodificar tokens de acceso JWT.
        JWT_SECRET_KEY: str = "CHANGE_ME"
        JWT_ALGORITHM: str = "HS256"

    # Instancia el objeto global de configuraciones.
    settings = Settings()
