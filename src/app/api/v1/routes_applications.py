"""
Define los endpoints para la gestión de solicitudes de inscripción (Applications).
Permite crear solicitudes, listar las propias peticiones, actualizar estados, eliminar/cancelar solicitudes y exportar registros en Excel.
"""

from datetime import date
from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_db
from app.models.application import Application
from app.models.course import Course
from app.models.user import User
from app.schemas.application_schema import (
    ApplicationCreate,
    ApplicationDetailRead,
    ApplicationRead,
    ApplicationStatusUpdate,
)
from app.utils.decorators import require_auth, require_role
from app.utils.enums import ApplicationStatus, Role
from app.utils.excel import build_applications_excel

router = APIRouter()


@router.post("/", response_model=ApplicationRead, status_code=status.HTTP_201_CREATED)
def create_application(
    application_in: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth),
):
    """
    Crea una nueva solicitud de inscripción para un curso.
    Valida DNI/NIE, mayoría de edad, vigencia del curso, duplicados y cupo máximo.
    """
    user_id = current_user.get("id")
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if not user.dni_nie:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must have a registered DNI/NIE to apply",
        )

    import re

    if not re.match(r"^(?:\d{8}[A-Z]|[XYZ]\d{7}[A-Z])$", user.dni_nie, re.IGNORECASE):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User DNI/NIE has an invalid format",
        )

    if not user.birth_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must have a registered birth date to apply",
        )

    from datetime import timedelta

    if user.birth_date > (date.today() - timedelta(days=18 * 365.25)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be at least 18 years old to apply",
        )

    course = db.get(Course, application_in.course_id)

    if not course or not course.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course not available",
        )
    if date.today() >= course.start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Application period has ended",
        )

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
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course is full",
        )

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
    """Lista las solicitudes del usuario autenticado actual."""
    user_id = current_user.get("id")
    return db.query(Application).filter(Application.user_id == user_id).all()


@router.get("/", response_model=list[ApplicationDetailRead])
def get_all_applications(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role([Role.ADMIN])),
):
    """Lista todas las solicitudes del sistema con datos del usuario y del curso."""
    return (
        db.query(Application)
        .join(Application.user)
        .options(joinedload(Application.user), joinedload(Application.course))
        .all()
    )


@router.get(
    "/export/excel",
    response_class=StreamingResponse,
)
def export_applications_excel(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role([Role.ADMIN])),
):
    """
    Exporta las solicitudes de inscripción en formato Excel.
    """
    applications = (
        db.query(Application)
        .options(joinedload(Application.user), joinedload(Application.course))
        .order_by(Application.id.desc())
        .all()
    )

    excel_bytes = build_applications_excel(applications)
    filename = f"solicitudes_{date.today().isoformat()}.xlsx"

    return StreamingResponse(
        BytesIO(excel_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.patch("/{app_id}/status", response_model=ApplicationRead)
def update_application_status(
    app_id: int,
    status_update: ApplicationStatusUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role([Role.ADMIN])),
):
    """Actualiza el estado de una solicitud específica."""
    app_obj = db.get(Application, app_id)
    if not app_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
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
    """Elimina físicamente una solicitud si es admin o cancela si es el propio usuario."""
    app_obj = db.get(Application, app_id)
    if not app_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    user_role = current_user.get("role")
    user_id = current_user.get("id")

    if user_role in [Role.ADMIN.value, Role.SUPERADMIN.value]:
        db.delete(app_obj)
        db.commit()
        response.status_code = status.HTTP_204_NO_CONTENT
        return None

    if app_obj.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

    app_obj.status = ApplicationStatus.CANCELLED
    db.commit()
    db.refresh(app_obj)
    return app_obj