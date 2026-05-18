from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models.user import User
from app.models.token_blacklist import TokenBlacklist
from app.schemas.auth_schema import LoginRequest
from app.schemas.user_schema import UserCreate, UserRead
from app.core.security import verify_password, create_access_token, hash_password
from app.utils.decorators import require_auth

router = APIRouter()

# Nombre de la cookie para el token
COOKIE_NAME = "access_token"

@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    exists = db.query(User).filter(User.email == user_in.email).first()
    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail="Email already registered"
        )

    user = User(
        name=user_in.name,
        email=user_in.email,
        password=hash_password(user_in.password),
        role=user_in.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login")
def login(data: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid credentials"
        )

    token = create_access_token({"user_id": user.id, "role": user.role})
    
    # Establecer la cookie HttpOnly
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        secure=False,  # Cambiar a True en producción con HTTPS
        samesite="lax",
        max_age=3600  # 1 hora
    )
    
    return {"message": "Logged in successfully"}

@router.post("/logout")
def logout(request: Request, response: Response, db: Session = Depends(get_db), user: dict = Depends(require_auth)):
    # Extraer el token de las cookies para invalidarlo
    token = request.cookies.get(COOKIE_NAME)
    
    if token:
        # Registrar el token en la lista negra
        blacklisted = TokenBlacklist(token=token)
        db.add(blacklisted)
        db.commit()
    
    # Eliminar la cookie del navegador
    response.delete_cookie(COOKIE_NAME)
    
    return {"message": "Logged out successfully"}
