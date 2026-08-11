from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.appointments import service
from app.api.appointments.schemas import (
    AppointmentCreate,
    AppointmentResponse,
    AppointmentUpdate,
)
from app.database.session import get_db


router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"],
)


@router.post(
    "/",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_appointment(
    appointment_data: AppointmentCreate,
    db: Session = Depends(get_db),
):
    return service.create_appointment(db=db, appointment_data=appointment_data)


@router.get(
    "/",
    response_model=list[AppointmentResponse],
)
def get_appointments(db: Session = Depends(get_db)):
    return service.get_appointments(db=db)


@router.get(
    "/{appointment_id}",
    response_model=AppointmentResponse,
)
def get_appointment(appointment_id: int, db: Session = Depends(get_db)):
    appointment = service.get_appointment(db=db, appointment_id=appointment_id)
    if appointment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )
    return appointment


@router.put(
    "/{appointment_id}",
    response_model=AppointmentResponse,
)
def update_appointment(
    appointment_id: int,
    appointment_data: AppointmentUpdate,
    db: Session = Depends(get_db),
):
    appointment = service.update_appointment(
        db=db,
        appointment_id=appointment_id,
        appointment_data=appointment_data,
    )
    if appointment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )
    return appointment


@router.delete(
    "/{appointment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    appointment = service.delete_appointment(db=db, appointment_id=appointment_id)
    if appointment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )
    return None
