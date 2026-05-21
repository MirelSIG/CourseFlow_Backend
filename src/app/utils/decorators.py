"""
Define decoradores y dependencias para el control de acceso y autorización.
Implementa validación de tokens basada en cookies y un sistema jerárquico de roles.
"""

import os
from fastapi import Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.api.deps import get_db
from app.models.token_blacklist import TokenBlacklist
from app.utils.errors import error_response, forbidden_error
from app.utils.enums import Role

from app.core.config import settings

SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM

# Jerarquía de roles: user < admin < superadmin
ROLE_HIERARCHY = {
    Role.USER.value: 1,
    Role.ADMIN.value: 2,
    Role.SUPERADMIN.value: 3
}

async def require_auth(
    request: Request, 
    db: Session = Depends(get_db)
):
    """
    Dependencia de FastAPI que extrae el token JWT de las cookies del navegador,
    valida su integridad, expiración y si está en la lista negra.
    """
    # Extrae el token de la cookie.
    token_str = request.cookies.get("access_token")
    
    # Valida si no se proporcionó el token.
    if not token_str:
        error_response(401, "Missing authentication cookie")
        
    # Verifica si el token ha sido revocado comprobando la lista negra en la base de datos.
    is_blacklisted = db.query(TokenBlacklist).filter(TokenBlacklist.token == token_str).first()
    if is_blacklisted:
        error_response(401, "Token has been revoked")

    try:
        # Decodifica el token usando la clave secreta y el algoritmo configurado.
        payload = jwt.decode(token_str, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Extrae los datos relevantes del payload.
        user_id = payload.get("user_id")
        role = payload.get("role")
        
        # Valida que los datos existan en el payload.
        if user_id is None or role is None:
            error_response(401, "Invalid token payload")
            
        # Inyecta la identidad en el estado de la petición (request.state).
        # Esto permite que los controladores accedan al usuario sin decodificar de nuevo.
        request.state.current_user = {
            "id": user_id,
            "role": role
        }
        
        return request.state.current_user
    except jwt.ExpiredSignatureError:
        error_response(401, "Token has expired")
    except JWTError:
        error_response(401, "Invalid token")

def require_role(roles: list[Role]):
    """
    Generador de dependencia que comprueba que el usuario autenticado tiene permisos
    suficientes basados en una lista de roles permitidos y su jerarquía.
    """
    def role_checker(request: Request, user: dict = Depends(require_auth)):
        # Extrae el rol del usuario que se inyectó en la dependencia require_auth.
        user_role = user.get("role")
        
        # Obtiene el nivel numérico del rol del usuario (por defecto 0 si no existe).
        user_level = ROLE_HIERARCHY.get(user_role, 0)
        
        # Normaliza la lista de roles permitidos obteniendo su valor si es un Enum.
        allowed_roles = [r.value if hasattr(r, "value") else r for r in roles]
        
        # Obtiene el nivel numérico mínimo requerido para acceder a la ruta.
        min_required_level = min(
            [ROLE_HIERARCHY.get(r, 99) for r in allowed_roles], 
            default=99
        )
        
        # Lógica de Jerarquía: si el nivel del usuario es igual o mayor al mínimo requerido, permite el acceso.
        # Esto garantiza que un superadmin (nivel 3) pueda entrar a rutas de admin (nivel 2).
        if user_level >= min_required_level:
            return user
            
        # Si no cumple el nivel jerárquico, se retorna un error 403 Forbidden.
        forbidden_error()
        
    return role_checker

async def optional_auth(
    request: Request, 
    db: Session = Depends(get_db)
):
    """
    Dependencia de FastAPI que intenta extraer y validar el token JWT de las cookies.
    Si el token no está presente, está en la lista negra o es inválido,
    retorna None en lugar de lanzar una excepción HTTP 401.
    """
    token_str = request.cookies.get("access_token")
    if not token_str:
        return None
        
    is_blacklisted = db.query(TokenBlacklist).filter(TokenBlacklist.token == token_str).first()
    if is_blacklisted:
        return None

    try:
        payload = jwt.decode(token_str, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        role = payload.get("role")
        
        if user_id is None or role is None:
            return None
            
        request.state.current_user = {
            "id": user_id,
            "role": role
        }
        return request.state.current_user
    except JWTError:
        return None

