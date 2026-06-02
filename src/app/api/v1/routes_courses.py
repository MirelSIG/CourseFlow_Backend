"""
Define los endpoints para la gestión de cursos.
Permite crear, listar, consultar, actualizar y realizar bajas lógicas de cursos.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models.course import Course
from app.schemas.course_schema import CourseCreate, CourseUpdate, CourseRead
from app.utils.decorators import require_auth, require_role, optional_auth
from app.utils.enums import Role
from app.models.application import Application
from app.schemas.application_schema import ApplicationDetailRead

router = APIRouter(tags=["courses"])

@router.post("/", response_model=CourseRead, status_code=status.HTTP_201_CREATED)
def create_course(
    course_in: CourseCreate, 
    db: Session = Depends(get_db),
    user: dict = Depends(require_role([Role.ADMIN]))
):
    """
    Crea un nuevo curso en el sistema. Requiere privilegios de administrador.
    Valida que la fecha de finalización sea posterior a la fecha de inicio.
    """
    if course_in.end_date <= course_in.start_date:
        raise HTTPException(status_code=422, detail="end_date must be strictly after start_date")
        
    course = Course(**course_in.model_dump())
    db.add(course)
    db.commit()
    db.refresh(course)
    return course

@router.get("/", response_model=list[CourseRead])
def list_courses(
    db: Session = Depends(get_db),
    user: dict | None = Depends(optional_auth)
):
    """
    Lista los cursos disponibles.
    Permite a los administradores ver todos los cursos, y a los usuarios estándar
    o no autenticados ver solo los activos.
    """
    # Si no está autenticado, solo ve los activos.
    if not user:
        return db.query(Course).filter(Course.is_active.is_(True)).all()
    # Administradores y Superadmins ven todos los cursos.
    if user.get("role") in [Role.ADMIN.value, Role.SUPERADMIN.value]:
        return db.query(Course).all()
    # Usuarios normales solo ven los activos.
    return db.query(Course).filter(Course.is_active.is_(True)).all()

@router.get(
    "/catalog",
    response_model=list[CourseRead],
    tags=["courses"],
    summary="Catálogo público de cursos",
    description="Devuelve únicamente los cursos activos, sin requerir autenticación.",
    response_description="Lista de cursos activos disponibles en el catálogo.",
)
def list_catalog_courses(
    db: Session = Depends(get_db),
):
    """
    Lista los cursos disponibles en el catálogo público.
    Solo devuelve cursos activos, sin distinguir entre tipos de usuario.
    """
    return db.query(Course).filter(Course.is_active.is_(True)).all()

@router.get("/{course_id}", response_model=CourseRead)
def get_course(
    course_id: int, 
    db: Session = Depends(get_db),
    user: dict | None = Depends(optional_auth)
):
    """
    Obtiene los detalles de un curso por su identificador.
    Impide que los usuarios estándar y visitantes no autenticados accedan a cursos inactivos.
    """
    course = db.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    # Si no está autenticado o es un usuario normal, no puede ver un curso inactivo.
    if not user or user.get("role") == Role.USER.value:
        if not course.is_active:
            raise HTTPException(status_code=404, detail="Course not found")
        
    return course

@router.get("/{course_id}/applications", response_model=list[ApplicationDetailRead])
def get_course_applications(
    course_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_role([Role.ADMIN]))
):
    """
    Recupera todas las solicitudes de inscripción asociadas a un curso específico. Requiere privilegios de administrador.
    """
    course = db.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    return db.query(Application).filter(Application.course_id == course_id).all()

@router.put("/{course_id}", response_model=CourseRead)
def update_course(
    course_id: int, 
    course_in: CourseUpdate, 
    db: Session = Depends(get_db),
    user: dict = Depends(require_role([Role.ADMIN]))
):
    """
    Actualiza la información de un curso existente. Requiere privilegios de administrador.
    Valida la coherencia de las nuevas fechas de inicio y finalización.
    """
    course = db.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    new_start_date = course_in.start_date if course_in.start_date is not None else course.start_date
    new_end_date = course_in.end_date if course_in.end_date is not None else course.end_date
    
    if new_end_date <= new_start_date:
        raise HTTPException(status_code=422, detail="end_date must be strictly after start_date")

    for field, value in course_in.model_dump(exclude_unset=True).items():
        setattr(course, field, value)

    db.commit()
    db.refresh(course)
    return course

@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(
    course_id: int, 
    db: Session = Depends(get_db),
    user: dict = Depends(require_role([Role.ADMIN]))
):
    """
    Realiza una baja lógica de un curso del sistema cambiando su estado a inactivo. Requiere privilegios de administrador.
    """
    course = db.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    course.is_active = False
    db.commit()
    return None
