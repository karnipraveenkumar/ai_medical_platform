from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.doctor import schemas, service
from app.database.session import get_db


router = APIRouter(
    prefix="/doctors",
    tags=["Doctors"],
)


@router.post(
    "/",
    response_model=schemas.DoctorResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_doctor(
    doctor_data: schemas.DoctorCreate,
    db: Session = Depends(get_db),
):
    return service.create_doctor(db=db, doctor_data=doctor_data)


@router.get(
    "/",
    response_model=list[schemas.DoctorResponse],
)
def get_doctors(db: Session = Depends(get_db)):
    return service.get_doctors(db=db)


@router.get(
    "/{doctor_id}",
    response_model=schemas.DoctorResponse,
)
def get_doctor(doctor_id: int, db: Session = Depends(get_db)):
    doctor = service.get_doctor(db=db, doctor_id=doctor_id)
    if doctor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found",
        )
    return doctor


@router.put(
    "/{doctor_id}",
    response_model=schemas.DoctorResponse,
)
def update_doctor(
    doctor_id: int,
    doctor_data: schemas.DoctorUpdate,
    db: Session = Depends(get_db),
):
    doctor = service.update_doctor(
        db=db,
        doctor_id=doctor_id,
        doctor_data=doctor_data,
    )
    if doctor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found",
        )
    return doctor


@router.delete(
    "/{doctor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_doctor(doctor_id: int, db: Session = Depends(get_db)):
    doctor = service.delete_doctor(db=db, doctor_id=doctor_id)
    if doctor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found",
        )
    return None
