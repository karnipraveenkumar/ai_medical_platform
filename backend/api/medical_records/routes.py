from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.medical_records import service
from app.api.medical_records.schemas import (
    MedicalRecordCreate,
    MedicalRecordResponse,
    MedicalRecordUpdate,
)
from app.database.session import get_db


router = APIRouter(
    prefix="/medical-records",
    tags=["Medical Records"],
)


@router.post(
    "/",
    response_model=MedicalRecordResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_medical_record(
    medical_record_data: MedicalRecordCreate,
    db: Session = Depends(get_db),
):
    return service.create_medical_record(db=db, medical_record_data=medical_record_data)


@router.get(
    "/",
    response_model=list[MedicalRecordResponse],
)
def get_medical_records(db: Session = Depends(get_db)):
    return service.get_medical_records(db=db)


@router.get(
    "/{medical_record_id}",
    response_model=MedicalRecordResponse,
)
def get_medical_record(medical_record_id: int, db: Session = Depends(get_db)):
    record = service.get_medical_record(db=db, medical_record_id=medical_record_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical record not found",
        )
    return record


@router.put(
    "/{medical_record_id}",
    response_model=MedicalRecordResponse,
)
def update_medical_record(
    medical_record_id: int,
    medical_record_data: MedicalRecordUpdate,
    db: Session = Depends(get_db),
):
    record = service.update_medical_record(
        db=db,
        medical_record_id=medical_record_id,
        medical_record_data=medical_record_data,
    )
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical record not found",
        )
    return record


@router.delete(
    "/{medical_record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_medical_record(medical_record_id: int, db: Session = Depends(get_db)):
    record = service.delete_medical_record(db=db, medical_record_id=medical_record_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical record not found",
        )
    return None
