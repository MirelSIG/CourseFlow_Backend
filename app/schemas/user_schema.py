from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from typing import Optional
from datetime import date, timedelta
import re

class UserBase(BaseModel):
    name: str
    email: EmailStr
    dni_nie: Optional[str] = None
    birth_date: Optional[date] = None

    @field_validator("dni_nie")
    def validate_dni_nie(cls, v):
        if v is None:
            return v
        # Simple validation for DNI (8 digits + 1 letter) or NIE (X/Y/Z + 7 digits + 1 letter)
        if not re.match(r"^(?:\d{8}[A-Z]|[XYZ]\d{7}[A-Z])$", v, re.IGNORECASE):
            raise ValueError("Invalid DNI/NIE format")
        return v.upper()

    @field_validator("birth_date")
    def validate_age(cls, v):
        if v is None:
            return v
        if v > (date.today() - timedelta(days=18*365.25)):
            raise ValueError("User must be at least 18 years old")
        return v

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int
    role: str
    model_config = ConfigDict(from_attributes=True)
