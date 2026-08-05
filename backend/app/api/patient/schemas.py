from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class PatientCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    age: int = Field(ge=0, le=130)
    gender: str = Field(min_length=1, max_length=20)
    phone: str | None = None
    email: EmailStr | None = None
    medical_history: str | None = None


class PatientUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    age: int = Field(ge=0, le=130)
    gender: str = Field(min_length=1, max_length=20)
    phone: str | None = None
    email: EmailStr | None = None
    medical_history: str | None = None


class PatientResponse(BaseModel):
    id: int
    name: str
    age: int
    gender: str
    phone: str | None = None
    email: EmailStr | None = None
    medical_history: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
