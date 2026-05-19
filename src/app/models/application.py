"""
Define el modelo Application que representa las solicitudes de inscripción de los estudiantes.
Garantiza peticiones únicas por usuario y curso, valida campos adjuntos y mapea relaciones.
"""

from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint, Enum as SQLEnum, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
from app.utils.enums import ApplicationStatus

class Application(Base):
    """
    Representa una solicitud de inscripción enviada por un usuario para un curso específico.
    """
    __tablename__ = "applications"
    
    # Asegura una restricción de unicidad para que un usuario no solicite el mismo curso múltiples veces.
    __table_args__ = (
        UniqueConstraint("user_id", "course_id", name="uq_user_course_application"),
    )

    # Identificador único de la solicitud.
    id = Column(Integer, primary_key=True, index=True)
    
    # Identificador que hace referencia al usuario (User) solicitante.
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Identificador que hace referencia al curso (Course) solicitado.
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    
    # Estado actual de la solicitud (PENDIENTE, ACEPTADA, RECHAZADA).
    status = Column(SQLEnum(ApplicationStatus), nullable=False, default=ApplicationStatus.PENDING)
    
    # Bandera que indica si el solicitante posee un documento DARDE (desempleo) válido.
    has_darde = Column(Boolean, nullable=True)
    
    # Resumen de los estudios previos o formación del solicitante.
    previous_education = Column(Text, nullable=True)
    
    # Marcas de tiempo de creación y modificación de la solicitud.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones para acceder a los datos completos del solicitante y del curso.
    user = relationship("User", back_populates="applications")
    course = relationship("Course", back_populates="applications")
