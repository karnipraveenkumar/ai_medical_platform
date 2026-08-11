from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class DoctorCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    specialty: str | None = None
    email: EmailStr
    phone: str | None = None


class DoctorUpdate(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    specialty: str | None = None
    phone: str | None = None


class DoctorResponse(BaseModel):
    id: int
    full_name: str
    specialty: str | None = None
    email: EmailStr
    phone: str | None = None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
