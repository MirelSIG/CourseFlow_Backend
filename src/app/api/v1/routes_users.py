from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.utils.decorators import require_auth
from app.models.user import User
from app.schemas.user_schema import UserRead, UserUpdate

router = APIRouter()

@router.get("/me", response_model=UserRead)
def get_me(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """
    Retorna el perfil del usuario autenticado actual.
    """
    user_id = current_user.get("id")
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.patch("/me", response_model=UserRead)
def update_me(
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """
    Actualiza datos de perfil del usuario autenticado actual.
    """
    user_id = current_user.get("id")
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_in.email is not None and user_in.email != user.email:
        # Validar si el email ya existe
        existing_user = db.query(User).filter(User.email == user_in.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        user.email = user_in.email

    if user_in.name is not None:
        user.name = user_in.name

    if user_in.dni_nie is not None:
        user.dni_nie = user_in.dni_nie

    if user_in.birth_date is not None:
        user.birth_date = user_in.birth_date

    db.commit()
    db.refresh(user)
    return user
