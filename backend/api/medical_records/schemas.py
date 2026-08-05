from datetime import date

from pydantic import BaseModel, ConfigDict


class MedicalRecordBase(BaseModel):
    patient_id: int
    doctor_id: int | None = None
    record_type: str
    description: str | None = None
    record_date: date | None = None


class MedicalRecordCreate(MedicalRecordBase):
    pass


class MedicalRecordUpdate(MedicalRecordBase):
    pass


class MedicalRecordResponse(MedicalRecordBase):
    id: int
    created_at: str

    model_config = ConfigDict(from_attributes=True)
