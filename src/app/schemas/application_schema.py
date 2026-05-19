from pydantic import BaseModel, constr, ConfigDict
from typing import Optional

class ApplicationBase(BaseModel):
    course_id: int
    has_darde: bool
    previous_education: Optional[constr(max_length=250)] = None

class ApplicationCreate(ApplicationBase):
    pass

from app.utils.enums import ApplicationStatus

class ApplicationRead(ApplicationBase):
    id: int
    user_id: int
    status: str
    model_config = ConfigDict(from_attributes=True)

class UserShort(BaseModel):
    name: str
    email: str
    model_config = ConfigDict(from_attributes=True)

class ApplicationDetailRead(ApplicationRead):
    user: UserShort

class ApplicationStatusUpdate(BaseModel):
    status: ApplicationStatus
