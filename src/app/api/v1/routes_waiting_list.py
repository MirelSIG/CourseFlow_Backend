from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.api.deps import get_db
from app.models.waiting_list import WaitingList

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
def add_to_waiting_list(user_id: int, course_id: int, db: Session = Depends(get_db)):
    max_pos = (
        db.query(func.max(WaitingList.position))
        .filter(WaitingList.course_id == course_id)
        .scalar()
        or 0
    )

    entry = WaitingList(
        user_id=user_id,
        course_id=course_id,
        position=max_pos + 1,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

@router.get("/{course_id}")
def list_waiting_list(course_id: int, db: Session = Depends(get_db)):
    return (
        db.query(WaitingList)
        .filter(WaitingList.course_id == course_id)
        .order_by(WaitingList.position.asc())
        .all()
    )
