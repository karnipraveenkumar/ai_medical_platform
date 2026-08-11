from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AppointmentBase(BaseModel):
    patient_id: int
    doctor_id: int
    start_time: datetime
    end_time: datetime
    reason: str | None = None


class AppointmentCreate(AppointmentBase):
    pass


class AppointmentUpdate(AppointmentBase):
    is_confirmed: bool = False


class AppointmentResponse(AppointmentBase):
    id: int
    is_confirmed: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
