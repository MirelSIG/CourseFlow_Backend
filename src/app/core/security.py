"""
Proporciona funciones de utilidad de seguridad para el hashing de contraseñas,
su verificación y la creación de JSON Web Tokens (JWT).
"""

import bcrypt
from datetime import datetime, timedelta
from jose import jwt
from app.core.config import settings

def hash_password(password: str) -> str:
    """
    Genera un hash de una contraseña en texto plano utilizando bcrypt.
    Codifica la cadena a bytes, genera una sal segura, realiza el hashing y decodifica a UTF-8.
    """
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    return hashed_password.decode('utf-8')


def verify_password(plain: str, hashed: str) -> bool:
    """
    Verifica una contraseña en texto plano frente a un hash almacenado de bcrypt.
    Retorna True si las credenciales coinciden, False en caso contrario.
    """
    password_byte_enc = plain.encode('utf-8')
    hashed_byte_enc = hashed.encode('utf-8')
    return bcrypt.checkpw(password_byte_enc, hashed_byte_enc)


def create_access_token(data: dict, expires_minutes: int = 60) -> str:
    """
    Genera un nuevo token de acceso JWT firmado codificando las declaraciones (claims) del diccionario.
    Establece automáticamente la fecha de expiración del token basada en la hora UTC actual.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
