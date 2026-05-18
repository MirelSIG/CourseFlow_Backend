from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models.user import User
from app.schemas.user_schema import UserCreate, UserRead
from app.core.security import hash_password

router = APIRouter()

@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    exists = db.query(User).filter(User.email == user_in.email).first()
    if exists:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        name=user_in.name,
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        role="user",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
