"""
Define funciones auxiliares comunes para la inyección de dependencias en los endpoints de FastAPI.
Incluye la gestión del ciclo de vida de las sesiones de base de datos y herramientas de autenticación del usuario.
"""

from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.core.config import settings
from app.models.user import User
from app.models.token_blacklist import TokenBlacklist


def get_db() -> Generator:
    """
    Proporciona una instancia de sesión de base de datos para usar dentro del ciclo de vida de la petición.
    Cierra la sesión automáticamente después de finalizar la petición.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Establece el esquema de seguridad OAuth2 con token portador (bearer token) para la extracción de credenciales.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Valida el token portador, comprueba las listas de revocación y recupera el usuario autenticado.
    Lanza una excepción HTTP 401 Unauthorized si la validación de credenciales falla.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    try:
        # Decodifica el token de acceso JWT para recuperar el payload de identidad.
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        user_id: str | None = payload.get("sub")
        jti: str | None = payload.get("jti")
        if user_id is None or jti is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Comprueba la lista negra de tokens para verificar si el token actual ha sido revocado.
    blacklisted = (
        db.query(TokenBlacklist)
        .filter(TokenBlacklist.token == token)
        .first()
    )
    if blacklisted:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token revoked",
        )

    # Recupera al usuario asociado al sujeto del token decodificado.
    user = db.get(User, int(user_id))
    if not user:
        raise credentials_exception

    return user
