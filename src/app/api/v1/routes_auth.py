"""
Define los endpoints para el flujo de autenticación de la aplicación (registro, inicio y cierre de sesión).
Utiliza cookies HttpOnly para el almacenamiento seguro del token JWT.
"""

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

# Nombre de la cookie para almacenar el token de acceso.
COOKIE_NAME = "access_token"

@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Registra un nuevo usuario en el sistema.
    Valida que el correo electrónico no esté previamente registrado.
    """
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
    """
    Autentica a un usuario verificando sus credenciales de acceso.
    Genera un token JWT y lo almacena en una cookie HttpOnly para mayor seguridad.
    """
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid credentials"
        )

    token = create_access_token({"user_id": user.id, "role": user.role})
    
    # Establece la cookie HttpOnly en la respuesta HTTP.
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        secure=False,  # Debe cambiarse a True en producción bajo HTTPS.
        samesite="lax",
        max_age=3600  # Duración de 1 hora.
    )
    
    return {"message": "Logged in successfully"}

@router.post("/logout")
def logout(request: Request, response: Response, db: Session = Depends(get_db), user: dict = Depends(require_auth)):
    """
    Cierra la sesión del usuario invalidando el token actual.
    Registra el token en la lista negra (TokenBlacklist) y elimina la cookie del navegador.
    """
    # Extrae el token de las cookies para invalidarlo.
    token = request.cookies.get(COOKIE_NAME)
    
    if token:
        # Registra el token en la lista negra para evitar su reutilización.
        blacklisted = TokenBlacklist(token=token)
        db.add(blacklisted)
        db.commit()
    
    # Elimina la cookie de sesión en el navegador.
    response.delete_cookie(COOKIE_NAME)
    
    return {"message": "Logged out successfully"}
