"""
Define el modelo Course que representa la información estructural de los cursos.
Soporta límites de inscripción, visibilidad de los cursos y bajas lógicas.
"""

from sqlalchemy import Column, Integer, String, Text, Date, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Course(Base):
    """
    Representa una entidad de curso en la base de datos.
    Almacena metadatos sobre fechas, disponibilidad, estado y solicitudes de inscripción.
    """
    __tablename__ = "courses"

    # Identificador único del curso.
    id = Column(Integer, primary_key=True, index=True)
    
    # Nombre o título del curso.
    name = Column(String(150), nullable=False)
    
    # Resumen detallado del curso o temario.
    description = Column(Text)
    
    # Fecha de inicio programada del curso.
    start_date = Column(Date, nullable=False)
    
    # Fecha de finalización programada del curso.
    end_date = Column(Date, nullable=False)
    
    # Número máximo permitido de estudiantes matriculados.
    capacity = Column(Integer)
    
    # Bandera de estado activo; permite bajas lógicas al cambiar a False.
    is_active = Column(Boolean, default=True)
    
    # Marcas de tiempo de creación y actualización del curso.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relación de uno a muchos con Application; elimina las solicitudes asociadas si el curso se elimina.
    applications = relationship("Application", back_populates="course", cascade="all, delete-orphan")
