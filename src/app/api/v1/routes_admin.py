from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.utils.decorators import require_role
from app.utils.enums import Role
from app.models.user import User
from app.schemas.user_schema import AdminCreate, AdminUpdate, UserRead
from app.core.security import hash_password
from app.utils.errors import error_response

router = APIRouter(
    dependencies=[Depends(require_role([Role.SUPERADMIN]))]
)

@router.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_admin(
    admin_in: AdminCreate,
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo usuario con rol ADMIN. Exclusivo de SUPERADMIN.
    """
    # Validar si el email ya existe
    existing_user = db.query(User).filter(User.email == admin_in.email).first()
    if existing_user:
        error_response(status.HTTP_400_BAD_REQUEST, "Email already registered")
        
    new_admin = User(
        name=admin_in.name,
        email=admin_in.email,
        password=hash_password(admin_in.password),
        role=Role.ADMIN
    )
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    return new_admin

@router.get("/users", response_model=list[UserRead])
def list_admins(
    db: Session = Depends(get_db)
):
    """
    Devuelve la lista de usuarios con rol ADMIN. Exclusivo de SUPERADMIN.
    Excluye al propio Superadmin y a los usuarios normales.
    """
    admins = db.query(User).filter(User.role == Role.ADMIN).all()
    return admins

@router.patch("/users/{user_id}", response_model=UserRead)
def update_admin(
    user_id: int,
    admin_in: AdminUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza datos de un administrador. Exclusivo de SUPERADMIN.
    """
    admin = db.query(User).filter(User.id == user_id, User.role == Role.ADMIN).first()
    if not admin:
        error_response(status.HTTP_404_NOT_FOUND, "Admin not found")
        
    if admin_in.name is not None:
        admin.name = admin_in.name
        
    if admin_in.email is not None:
        # Validar si el email ya pertenece a otro usuario
        email_owner = db.query(User).filter(User.email == admin_in.email, User.id != user_id).first()
        if email_owner:
            error_response(status.HTTP_400_BAD_REQUEST, "Email already registered")
        admin.email = admin_in.email
        
    db.commit()
    db.refresh(admin)
    return admin

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_admin(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Elimina a un administrador. Exclusivo de SUPERADMIN.
    Evita la auto-eliminación.
    """
    # Extraer el ID del superadmin actual desde el estado de la petición
    current_user = request.state.current_user
    current_user_id = current_user.get("id")
    
    # Validar que el superadmin no se esté auto-eliminando
    if user_id == current_user_id:
        error_response(status.HTTP_400_BAD_REQUEST, "El superadmin no puede eliminarse a sí mismo")
        
    admin = db.query(User).filter(User.id == user_id, User.role == Role.ADMIN).first()
    if not admin:
        error_response(status.HTTP_404_NOT_FOUND, "Admin not found")
        
    db.delete(admin)
    db.commit()
    return
