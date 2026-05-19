"""
Define la clase base declarativa de SQLAlchemy.
Sirve como clase raíz para todos los modelos de mapeo relacional en la aplicación.
"""

from sqlalchemy.orm import declarative_base

# Instancia la clase Base compartida de la cual heredan todos los modelos de la base de datos.
Base = declarative_base()
