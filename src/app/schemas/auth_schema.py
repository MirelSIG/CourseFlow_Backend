"""
Define los esquemas de Pydantic para las solicitudes y respuestas de autenticación.
Gestiona el registro de usuarios, credenciales de inicio de sesión y el formato de serialización de tokens.
"""

from pydantic import BaseModel, EmailStr

class RegisterRequest(BaseModel):
    """
    Valida las solicitudes de registro de usuario, incluyendo especificaciones de roles.
    """
    name: str
    email: EmailStr
    password: str
    role: str = "user"

class LoginRequest(BaseModel):
    """
    Valida las credenciales del usuario durante el flujo de inicio de sesión.
    """
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    """
    Serializa los tokens de acceso JWT devueltos a los clientes.
    """
    access_token: str
    token_type: str = "bearer"

class LogoutResponse(BaseModel):
    """
    Formatea el mensaje de confirmación devuelto tras un cierre de sesión exitoso.
    """
    detail: str
