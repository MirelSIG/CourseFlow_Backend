from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.token_blacklist import TokenBlacklist
from app.schemas.auth_schema import RegisterRequest, LoginRequest, TokenResponse, LogoutResponse
from app.core.security import hash_password, verify_password, create_access_token
from jose import jwt
from app.core.config import settings

router = APIRouter()

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    if data.role not in ("user", "admin"):
        raise HTTPException(status_code=400, detail="Invalid role")

    user = User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
        role=data.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "email": user.email, "role": user.role}

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(user_id=user.id, role=user.role)
    return TokenResponse(access_token=token)

from fastapi import Header

@router.post("/logout", response_model=LogoutResponse)
def logout(
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    # Authorization: Bearer <token>
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    token = authorization.split(" ", 1)[1]

    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        jti: str = payload.get("jti")
        if not jti:
            raise HTTPException(status_code=401, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    exists = db.query(TokenBlacklist).filter(TokenBlacklist.jti == jti).first()
    if not exists:
        db.add(TokenBlacklist(jti=jti))
        db.commit()

    return LogoutResponse(detail="Logged out successfully")
