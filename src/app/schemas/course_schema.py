"""
Define los esquemas de Pydantic para la validación, actualización y serialización de datos de cursos.
"""

from pydantic import BaseModel, ConfigDict
from datetime import date

class CourseBase(BaseModel):
    """
    Sirve como esquema base para los datos del curso, compartiendo propiedades comunes.
    """
    name: str
    description: str | None = None
    start_date: date
    end_date: date
    capacity: int | None = None
    is_active: bool = True

class CourseCreate(CourseBase):
    """
    Valida la estructura de los datos enviados para registrar nuevos cursos.
    """
    pass

class CourseUpdate(BaseModel):
    """
    Valida las peticiones de actualización parcial de un curso. Todos los campos son opcionales.
    """
    name: str | None = None
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    capacity: int | None = None
    is_active: bool | None = None

class CourseRead(CourseBase):
    """
    Formatea la información del curso que se retorna a los clientes.
    """
    id: int
    model_config = ConfigDict(from_attributes=True)
