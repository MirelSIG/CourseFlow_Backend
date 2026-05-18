from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models.application import Application
from app.models.course import Course

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_application(user_id: int, course_id: int, db: Session = Depends(get_db)):
    course = db.get(Course, course_id)
    if not course or not course.is_active:
        raise HTTPException(status_code=400, detail="Course not available")

    exists = (
        db.query(Application)
        .filter(Application.user_id == user_id, Application.course_id == course_id)
        .first()
    )
    if exists:
        raise HTTPException(status_code=400, detail="Application already exists")

    app_obj = Application(user_id=user_id, course_id=course_id, status="pending")
    db.add(app_obj)
    db.commit()
    db.refresh(app_obj)
    return {"id": app_obj.id, "status": app_obj.status}

@router.patch("/{app_id}")
def update_application_status(app_id: int, status: str, db: Session = Depends(get_db)):
    app_obj = db.get(Application, app_id)
    if not app_obj:
        raise HTTPException(status_code=404, detail="Application not found")

    app_obj.status = status
    db.commit()
    db.refresh(app_obj)
    return {"id": app_obj.id, "status": app_obj.status}
