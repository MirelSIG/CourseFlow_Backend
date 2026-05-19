from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.api.deps import get_db, get_current_user
from app.models.application import Application
from app.models.course import Course
from app.models.user import User
from app.schemas.application_schema import ApplicationCreate, ApplicationRead
from datetime import date

router = APIRouter()

@router.post("/", response_model=ApplicationRead, status_code=status.HTTP_201_CREATED)
def create_application(
    application_in: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    course = db.get(Course, application_in.course_id)

    # 1. Validation of dates and visibility
    if not course or not course.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Course not available"
        )
    if date.today() >= course.start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Application period has ended",
        )

    # 2. Unique inscription validation
    existing_application = (
        db.query(Application)
        .filter(
            Application.user_id == current_user.id,
            Application.course_id == application_in.course_id,
        )
        .first()
    )
    if existing_application:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already applied to this course",
        )

    # 3. Capacity control
    accepted_count = (
        db.query(Application)
        .filter(
            Application.course_id == application_in.course_id,
            Application.status == "accepted",
        )
        .count()
    )
    if course.capacity > 0 and accepted_count >= course.capacity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Course is full"
        )

    # Create application
    app_obj = Application(
        **application_in.model_dump(), user_id=current_user.id, status="pending"
    )
    db.add(app_obj)
    db.commit()
    db.refresh(app_obj)
    return app_obj

@router.patch("/{app_id}", response_model=ApplicationRead)
def update_application_status(
    app_id: int,
    status_in: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 4. Role security
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action",
        )

    app_obj = db.get(Application, app_id)
    if not app_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )

    app_obj.status = status_in
    db.commit()
    db.refresh(app_obj)
    return app_obj
