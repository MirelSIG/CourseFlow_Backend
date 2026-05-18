from datetime import datetime, timedelta, timezone
from uuid import uuid4

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(user_id: int, role: str, expires_minutes: int = 60) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    jti = str(uuid4())

    to_encode = {
        "sub": str(user_id),
        "role": role,
        "exp": expire,
        "jti": jti,
    }

    return jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
