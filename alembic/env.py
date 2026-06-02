"""
Configuración del entorno de migraciones de Alembic.
Establece la conexión a la base de datos a partir de las variables de entorno
y configura la detección automática de metadatos de los modelos del sistema.
"""

from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
import os
import sys
from dotenv import load_dotenv

# Añade el directorio src al path de búsqueda de módulos.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))
load_dotenv()

# Objeto de configuración de Alembic, que proporciona acceso a los valores del archivo .ini.
config = context.config

# Interpreta el archivo de configuración para configurar los loggers.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Añade el objeto MetaData de los modelos para soporte de generación automática ('autogenerate').
from app.db.base import Base
from app.models.user import User
from app.models.course import Course
from app.models.application import Application

target_metadata = Base.metadata

# Establece la URL de conexión de SQLAlchemy a partir de la variable de entorno.
database_url = os.environ.get("DATABASE_URL", "sqlite:///./courseflow.db")
if database_url:
    config.set_main_option("sqlalchemy.url", database_url)


def run_migrations_offline() -> None:
    """
    Ejecuta las migraciones en modo 'offline' (sin conexión directa a la base de datos).
    Configura el contexto únicamente con una URL de conexión.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Ejecuta las migraciones en modo 'online' (conectándose directamente a la base de datos).
    Crea un motor de conexión y lo asocia al contexto de ejecución de Alembic.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
