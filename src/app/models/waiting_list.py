"""
Define el modelo WaitingList que representa las posiciones de los estudiantes en las listas de espera de los cursos llenos.
Garantiza pares únicos de usuario-curso y posiciones únicas en la cola de espera de cada curso.
"""

from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from app.db.base import Base

class WaitingList(Base):
    """
    Representa una entrada en la lista de espera para un curso.
    """
    __tablename__ = "waiting_list"
    
    # Asegura restricciones: un usuario solo ocupa un lugar por curso y no puede haber duplicados en la misma posición.
    __table_args__ = (
        UniqueConstraint("user_id", "course_id", name="uq_wait_user_course"),
        UniqueConstraint("course_id", "position", name="uq_wait_course_position"),
    )

    # Identificador único del registro de lista de espera.
    id = Column(Integer, primary_key=True, index=True)
    
    # Identificador que hace referencia al usuario (User) en espera.
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Identificador que hace referencia al curso (Course) solicitado.
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    
    # Posición numérica del usuario en la cola de espera (comienza en 1).
    position = Column(Integer, nullable=False)
    
    # Marca de tiempo de cuándo el usuario se unió a la lista de espera.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
