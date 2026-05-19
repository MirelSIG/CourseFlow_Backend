"""
Define los endpoints para la gestión de solicitudes de inscripción (Applications).
Permite crear solicitudes, listar las propias peticiones, actualizar estados y eliminar/cancelar solicitudes.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models.application import Application
from app.models.course import Course
from app.models.user import User
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
    """
    Crea una nueva solicitud de inscripción para un curso.
    Valida la existencia y vigencia del DNI/NIE del usuario, la mayoría de edad del solicitante,
    la vigencia del período de inscripción del curso, que no existan solicitudes duplicadas y la capacidad máxima del curso.
    """
    user_id = current_user.get("id")
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Valida la existencia de DNI/NIE en el perfil del usuario.
    if not user.dni_nie:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must have a registered DNI/NIE to apply"
        )
    
    import re
    if not re.match(r"^(?:\d{8}[A-Z]|[XYZ]\d{7}[A-Z])$", user.dni_nie, re.IGNORECASE):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User DNI/NIE has an invalid format"
        )

    # Valida la fecha de nacimiento (edad mínima de 18 años).
    if not user.birth_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must have a registered birth date to apply"
        )
    
    from datetime import timedelta
    if user.birth_date > (date.today() - timedelta(days=18*365.25)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be at least 18 years old to apply"
        )

    course = db.get(Course, application_in.course_id)

    # 1. Validación de fechas y estado activo del curso.
    if not course or not course.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Course not available"
        )
    if date.today() >= course.start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Application period has ended",
        )

    # 2. Validación de solicitud única (impide duplicados).
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

    # 3. Control de capacidad del curso (cupo disponible).
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

    # Crea y registra la solicitud de inscripción.
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
    Lista las solicitudes del usuario autenticado actual con su estado de procesamiento.
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
    """
    Actualiza el estado de una solicitud de inscripción específica. Requiere privilegios de administrador.
    """
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
    """
    Elimina físicamente una solicitud si es administrador o superadministrador.
    Realiza una cancelación lógica si la petición proviene del propio usuario solicitante.
    """
    app_obj = db.get(Application, app_id)
    if not app_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )

    user_role = current_user.get("role")
    user_id = current_user.get("id")

    if user_role in [Role.ADMIN.value, Role.SUPERADMIN.value]:
        # Realiza eliminación física en la base de datos si es administrador.
        db.delete(app_obj)
        db.commit()
        response.status_code = status.HTTP_204_NO_CONTENT
        return None
    else:
        # Realiza cancelación lógica si es el propio usuario solicitante.
        if app_obj.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        app_obj.status = ApplicationStatus.CANCELLED
        db.commit()
        db.refresh(app_obj)
        return app_obj
