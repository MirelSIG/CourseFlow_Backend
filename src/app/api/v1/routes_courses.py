from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models.course import Course
from app.schemas.course_schema import CourseCreate, CourseUpdate, CourseRead
from app.utils.decorators import require_auth, require_role
from app.utils.enums import Role
from app.models.application import Application
from app.schemas.application_schema import ApplicationDetailRead

router = APIRouter()

@router.post("/", response_model=CourseRead, status_code=status.HTTP_201_CREATED)
def create_course(
    course_in: CourseCreate, 
    db: Session = Depends(get_db),
    user: dict = Depends(require_role([Role.ADMIN]))
):
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
    user: dict = Depends(require_auth)
):
    # Administradores y Superadmins ven todos los cursos
    if user.get("role") in [Role.ADMIN.value, Role.SUPERADMIN.value]:
        return db.query(Course).all()
    # Usuarios normales solo ven los activos
    return db.query(Course).filter(Course.is_active.is_(True)).all()

@router.get("/{course_id}", response_model=CourseRead)
def get_course(
    course_id: int, 
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth)
):
    course = db.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    # Un usuario normal no puede ver un curso inactivo
    if user.get("role") == Role.USER.value and not course.is_active:
        raise HTTPException(status_code=404, detail="Course not found")
        
    return course

@router.get("/{course_id}/applications", response_model=list[ApplicationDetailRead])
def get_course_applications(
    course_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_role([Role.ADMIN]))
):
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
    course = db.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    course.is_active = False
    db.commit()
    return None
