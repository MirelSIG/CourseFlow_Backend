"""
Define el modelo TokenBlacklist para almacenar los tokens de acceso JWT revocados.
Proporciona capacidades de finalización de sesión (cierre de sesión/revocación) para evitar ataques de repetición.
"""

from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from app.db.base import Base

class TokenBlacklist(Base):
    """
    Representa un registro de token revocado.
    Cualquier petición entrante que presente un token en la lista negra es rechazada con un estado HTTP 401 Unauthorized.
    """
    __tablename__ = "token_blacklist"

    # Cadena del token original que actúa como clave primaria.
    token = Column(String(500), primary_key=True, index=True)
    
    # Marca de tiempo que registra cuándo se invalidó el token.
    blacklisted_at = Column(DateTime(timezone=True), server_default=func.now())
