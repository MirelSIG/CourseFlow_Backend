"""
Define los endpoints para gestionar la lista de espera de los cursos.
Permite añadir usuarios a la lista de espera y consultar los usuarios en espera ordenados por posición.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.api.deps import get_db
from app.models.waiting_list import WaitingList
from app.schemas.waiting_list_schema import WaitingListRead, WaitingListStatusUpdate
from app.utils.decorators import require_role
from app.utils.enums import Role

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
def add_to_waiting_list(user_id: int, course_id: int, db: Session = Depends(get_db)):
    """
    Añade un usuario a la lista de espera de un curso específico.
    Calcula de manera dinámica la siguiente posición de espera disponible en la cola..
    """
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
    """
    Recupera los registros de la lista de espera de un curso específico, ordenados de menor a mayor posición.
    """
    return (
        db.query(WaitingList)
        .filter(WaitingList.course_id == course_id)
        .order_by(WaitingList.position.asc())
        .all()
    )

@router.patch("/{app_id}/status", response_model=WaitingListRead)
def update_waiting_list_status(
    app_id: int,
    status_update: WaitingListStatusUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role([Role.ADMIN])),
):
    """
    Actualiza el estado de una solicitud de en espera específica. Requiere privilegios de administrador.
    """
    app_obj = db.get(WaitingList, app_id)
    if not app_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Waiting list entry not found"
        )

    app_obj.status = status_update.status
    db.commit()
    db.refresh(app_obj)
    return app_obj