"""
Inicializa el motor de base de datos SQLAlchemy y el registro de sesiones locales.
Gestiona las operaciones de base de datos dentro del backend de CourseFlow.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Configura argumentos de conexión específicos para SQLite que permiten soportar múltiples hilos.
connect_args = {"check_same_thread": False} if settings.SQLALCHEMY_DATABASE_URI.startswith("sqlite") else {}

# Instancia el motor (engine) para orquestar las conexiones a la base de datos objetivo.
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI, 
    connect_args=connect_args
)

# Configura la clase de sesión (SessionLocal) para las transacciones.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db(database_uri: str):
    """
    Reinicializa el motor global y la fábrica SessionLocal con el URI de base de datos especificado.
    Útil para sobrescribir configuraciones o conectarse a una base de datos de pruebas dinámicamente.
    """
    global engine, SessionLocal
    engine = create_engine(database_uri, pool_pre_ping=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
