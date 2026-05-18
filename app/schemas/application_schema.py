from pydantic import BaseModel, constr
from typing import Optional

class ApplicationBase(BaseModel):
    course_id: int
    has_darde: bool
    previous_education: Optional[constr(max_length=250)] = None

class ApplicationCreate(ApplicationBase):
    pass

class ApplicationRead(ApplicationBase):
    id: int
    user_id: int
    status: str

    class Config:
        from_attributes = True
