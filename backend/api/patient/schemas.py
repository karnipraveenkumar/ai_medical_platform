from datetime import date

from pydantic import BaseModel, ConfigDict, EmailStr


class PatientCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str | None = None
    date_of_birth: date | None = None


class PatientUpdate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str | None = None
    date_of_birth: date | None = None


class PatientResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    phone: str | None = None
    date_of_birth: date | None = None

    model_config = ConfigDict(from_attributes=True)