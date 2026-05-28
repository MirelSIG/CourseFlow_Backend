"""
Define los endpoints para gestionar la lista de espera de los cursos.
Permite añadir usuarios a la lista de espera y consultar los usuarios en espera ordenados por posición.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.api.deps import get_db
from app.models.waiting_list import WaitingList
from app.models.application import Application
from app.utils.enums import ApplicationStatus

router = APIRouter()

def _reindex_waiting_list(course_id: int, db: Session):
    """
    Reindexa las posiciones de la lista de espera para un curso específico.
    """
    entries = (
        db.query(WaitingList)
        .filter(WaitingList.course_id == course_id)
        .order_by(WaitingList.position.asc(), WaitingList.id.asc())
        .all()
    )
    for idx, entry in enumerate(entries):
        entry.position = idx + 1
    db.commit()

@router.post("/", status_code=status.HTTP_201_CREATED)
def add_to_waiting_list(user_id: int, course_id: int, db: Session = Depends(get_db)):
    """
    Añade un usuario a la lista de espera de un curso específico.
    Calcula de manera dinámica la siguiente posición de espera disponible en la cola.
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

@router.patch("/{entry_id}/pending", status_code=status.HTTP_200_OK)
def move_to_pending(entry_id: int, db: Session = Depends(get_db)):
    """
    Elimina un registro de la lista de espera y devuelve la solicitud asociada al estado PENDIENTE.
    """
    entry = db.get(WaitingList, entry_id)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Waiting list entry not found"
        )

    # Buscar la solicitud correspondiente
    application = (
        db.query(Application)
        .filter(
            Application.user_id == entry.user_id,
            Application.course_id == entry.course_id
        )
        .first()
    )
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )

    # Cambiar estado a PENDIENTE
    application.status = ApplicationStatus.PENDING
    
    # Eliminar de la lista de espera
    course_id = entry.course_id
    db.delete(entry)
    db.commit()

    # Reindexar la lista de espera para el curso
    _reindex_waiting_list(course_id, db)

    return {"detail": "Application restored to pending and waiting list entry removed"}

@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_waiting_entry(entry_id: int, db: Session = Depends(get_db)):
    """
    Elimina físicamente un registro de la lista de espera.
    """
    entry = db.get(WaitingList, entry_id)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Waiting list entry not found"
        )

    course_id = entry.course_id
    db.delete(entry)
    db.commit()

    # Reindexar la lista de espera para el curso
    _reindex_waiting_list(course_id, db)

    return None