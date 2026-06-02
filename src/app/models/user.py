"""
Define el modelo User que representa a los usuarios registrados en el sistema.
Incluye atributos de identificación, roles de autorización y referencias a relaciones.
"""

from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum, Date, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
from app.utils.enums import Role

class User(Base):
    """
    Representa una entidad de usuario en la base de datos.
    Almacena información personal, de autenticación y de autorización.
    """
    __tablename__ = "users"

    # Identificador único del usuario.
    id = Column(Integer, primary_key=True, index=True)
    
    # Nombre completo del usuario.
    name = Column(String(100), nullable=False)
    
    # Dirección de correo electrónico única utilizada como identificador de inicio de sesión.
    email = Column(String(150), unique=True, nullable=False, index=True)
    
    # Contraseña encriptada con bcrypt.
    password = Column(String(255), nullable=False)
    
    # Documento Nacional de Identidad (DNI) o Número de Identidad de Extranjero (NIE).
    dni_nie = Column(String(20), unique=True, nullable=True, index=True)
    
    # Fecha de nacimiento del usuario para verificar la edad mínima.
    birth_date = Column(Date, nullable=True)
    
    # Rol de control de acceso asignado al usuario.
    role = Column(SQLEnum(Role), nullable=False, default=Role.USER)

    # Bandera de estado del usuario; permite desactivación lógica sin borrar el registro.
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Marcas de tiempo que registran la creación y actualización del perfil.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relación de uno a muchos con Application; elimina las solicitudes asociadas si el usuario es eliminado.
    applications = relationship("Application", back_populates="user", cascade="all, delete-orphan")
