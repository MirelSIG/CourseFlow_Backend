from pydantic import BaseModel
from datetime import date

class CourseBase(BaseModel):
    name: str
    description: str | None = None
    start_date: date
    end_date: date
    capacity: int | None = None
    is_active: bool = True

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    capacity: int | None = None
    is_active: bool | None = None

class CourseRead(CourseBase):
    id: int

    class Config:
        from_attributes = True
