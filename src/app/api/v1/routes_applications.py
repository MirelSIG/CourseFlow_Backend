from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models.application import Application
from app.models.course import Course
from app.schemas.application_schema import ApplicationCreate, ApplicationRead, ApplicationStatusUpdate
from app.utils.decorators import require_auth, require_role
from app.utils.enums import Role, ApplicationStatus
from datetime import date

router = APIRouter()

@router.post("/", response_model=ApplicationRead, status_code=status.HTTP_201_CREATED)
def create_application(
    application_in: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth),
):
    user_id = current_user.get("id")
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
            Application.user_id == user_id,
            Application.course_id == application_in.course_id,
        )
        .first()
    )
    if existing_application:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already applied to this course",
        )

    # 3. Capacity control
    accepted_count = (
        db.query(Application)
        .filter(
            Application.course_id == application_in.course_id,
            Application.status == ApplicationStatus.ACCEPTED,
        )
        .count()
    )
    if course.capacity > 0 and accepted_count >= course.capacity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Course is full"
        )

    # Create application
    app_obj = Application(
        **application_in.model_dump(), user_id=user_id, status=ApplicationStatus.PENDING
    )
    db.add(app_obj)
    db.commit()
    db.refresh(app_obj)
    return app_obj

@router.get("/me", response_model=list[ApplicationRead])
def get_my_applications(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth),
):
    """
    Listar solicitudes del usuario autenticado con nombre del curso y estado actual.
    """
    user_id = current_user.get("id")
    return db.query(Application).filter(Application.user_id == user_id).all()

@router.patch("/{app_id}/status", response_model=ApplicationRead)
def update_application_status(
    app_id: int,
    status_update: ApplicationStatusUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role([Role.ADMIN])),
):
    app_obj = db.get(Application, app_id)
    if not app_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )

    app_obj.status = status_update.status
    db.commit()
    db.refresh(app_obj)
    return app_obj

@router.delete("/{app_id}")
def delete_application(
    app_id: int,
    response: Response,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth),
):
    app_obj = db.get(Application, app_id)
    if not app_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )

    user_role = current_user.get("role")
    user_id = current_user.get("id")

    if user_role in [Role.ADMIN.value, Role.SUPERADMIN.value]:
        # Physical delete
        db.delete(app_obj)
        db.commit()
        response.status_code = status.HTTP_204_NO_CONTENT
        return None
    else:
        # Soft cancel
        if app_obj.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        app_obj.status = ApplicationStatus.CANCELLED
        db.commit()
        db.refresh(app_obj)
        return app_obj
