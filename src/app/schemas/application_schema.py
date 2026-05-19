"""
Define los esquemas de Pydantic para las solicitudes de inscripción a los cursos.
Valida las solicitudes, las operaciones de lectura detalladas y las modificaciones de estado.
"""

from pydantic import BaseModel, constr, ConfigDict
from typing import Optional
from app.utils.enums import ApplicationStatus

class ApplicationBase(BaseModel):
    """
    Sirve como esquema base para el envío de solicitudes, compartiendo propiedades principales.
    """
    course_id: int
    has_darde: bool
    previous_education: Optional[constr(max_length=250)] = None

class ApplicationCreate(ApplicationBase):
    """
    Valida la estructura de los datos durante el envío de una solicitud de inscripción.
    """
    pass

class ApplicationRead(ApplicationBase):
    """
    Formatea la información general de la solicitud que se retorna en las respuestas tipo lista.
    """
    id: int
    user_id: int
    status: str
    model_config = ConfigDict(from_attributes=True)

class UserShort(BaseModel):
    """
    Formatea una representación condensada de los usuarios solicitantes.
    """
    name: str
    email: str
    model_config = ConfigDict(from_attributes=True)

class ApplicationDetailRead(ApplicationRead):
    """
    Extiende el esquema de lectura de solicitudes para incrustar datos detallados del usuario solicitante.
    """
    user: UserShort

class ApplicationStatusUpdate(BaseModel):
    """
    Valida las solicitudes de modificación de estado enviadas por los administradores.
    """
    status: ApplicationStatus
