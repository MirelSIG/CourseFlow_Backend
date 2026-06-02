"""
Define los esquemas de Pydantic para la validación, formateo y serialización de datos de usuarios.
Incluye validadores de campos personalizados para DNI/NIE y restricciones de edad del solicitante.
"""

from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from typing import Optional
from datetime import date, timedelta
import re

class UserBase(BaseModel):
    """
    Sirve como esquema base para los datos de usuario, compartiendo campos comunes.
    """
    name: str
    email: EmailStr
    dni_nie: Optional[str] = None
    birth_date: Optional[date] = None

    @field_validator("dni_nie")
    def validate_dni_nie(cls, v):
        """
        Valida el formato del DNI español (8 dígitos seguidos de 1 letra mayúscula)
        o NIE (letra X, Y o Z seguida de 7 dígitos y 1 letra mayúscula).
        Convierte automáticamente la cadena de entrada a mayúsculas.
        """
        if v is None:
            return v
        if not re.match(r"^(?:\d{8}[A-Z]|[XYZ]\d{7}[A-Z])$", v, re.IGNORECASE):
            raise ValueError("Invalid DNI/NIE format")
        return v.upper()

    @field_validator("birth_date")
    def validate_age(cls, v):
        """
        Impone la restricción de que el usuario debe ser mayor de 18 años.
        Utiliza 365.25 días por año para contemplar los años bisiestos.
        """
        if v is None:
            return v
        if v > (date.today() - timedelta(days=18*365.25)):
            raise ValueError("User must be at least 18 years old")
        return v

class UserCreate(UserBase):
    """
    Valida los datos de registro de un usuario, incluyendo contraseña y rol (por defecto "user").
    """
    password: str
    role: str = "user"

class UserRead(UserBase):
    """
    Formatea los datos del perfil de usuario que se retornan a los clientes.
    """
    id: int
    role: str
    is_active: bool
    model_config = ConfigDict(from_attributes=True)

class AdminCreate(BaseModel):
    """
    Valida las peticiones para la creación de administradores o superadministradores.
    """
    name: str
    email: EmailStr
    password: str

class AdminUpdate(BaseModel):
    """
    Valida las peticiones de actualización dirigidas a los perfiles de administrador.
    """
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None

class UserUpdate(BaseModel):
    """
    Valida las peticiones de actualización del propio perfil por parte de los usuarios normales.
    Incluye validación de campos para verificar el formato del documento de identidad y la edad.
    """
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    dni_nie: Optional[str] = None
    birth_date: Optional[date] = None

    @field_validator("dni_nie")
    def validate_dni_nie(cls, v):
        """
        Valida los formatos de DNI/NIE durante las actualizaciones de perfil.
        """
        if v is None:
            return v
        if not re.match(r"^(?:\d{8}[A-Z]|[XYZ]\d{7}[A-Z])$", v, re.IGNORECASE):
            raise ValueError("Invalid DNI/NIE format")
        return v.upper()

    @field_validator("birth_date")
    def validate_age(cls, v):
        """
        Asegura que el usuario sigue siendo mayor de 18 años tras actualizar su perfil.
        """
        if v is None:
            return v
        if v > (date.today() - timedelta(days=18*365.25)):
            raise ValueError("User must be at least 18 years old")
        return v

