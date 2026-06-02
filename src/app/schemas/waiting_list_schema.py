"""
Esquemas Pydantic para la lista de espera (WaitingList).
"""
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.utils.enums import ApplicationStatus


class WaitingListRead(BaseModel):
    id: int
    user_id: int
    course_id: int
    status: str
    position: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class WaitingListStatusUpdate(BaseModel):
    status: ApplicationStatus
