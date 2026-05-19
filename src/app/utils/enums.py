"""
Define los enums utilizados en toda la aplicación.
Incluye los roles de usuario y los estados de las solicitudes de inscripción.
"""

from enum import Enum

class Role(str, Enum):
    """
    Representa los roles de acceso disponibles para los usuarios.
    """
    USER = "user"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"

class ApplicationStatus(str, Enum):
    """
    Representa los posibles estados de una solicitud de inscripción.
    """
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
