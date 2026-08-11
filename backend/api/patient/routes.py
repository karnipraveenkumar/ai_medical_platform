from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.patient import service
from app.api.patient.schemas import (
    PatientCreate,
    PatientResponse,
    PatientUpdate
)
from app.database.session import get_db


router = APIRouter(
    prefix="/patients",
    tags=["Patients"]
)


@router.post(
    "/",
    response_model=PatientResponse,
    status_code=201
)
def create_patient(
    patient_data: PatientCreate,
    db: Session = Depends(get_db)
):
    return service.create_patient(
        db=db,
        patient_data=patient_data
    )


@router.get(
    "/",
    response_model=list[PatientResponse]
)
def get_all_patients(
    db: Session = Depends(get_db)
):
    return service.get_all_patients(
        db=db
    )


@router.get(
    "/{patient_id}",
    response_model=PatientResponse
)
def get_patient(
    patient_id: int,
    db: Session = Depends(get_db)
):
    patient = service.get_patient(
        db=db,
        patient_id=patient_id
    )

    if patient is None:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    return patient


@router.put(
    "/{patient_id}",
    response_model=PatientResponse
)
def update_patient(
    patient_id: int,
    patient_data: PatientUpdate,
    db: Session = Depends(get_db)
):
    patient = service.update_patient(
        db=db,
        patient_id=patient_id,
        patient_data=patient_data
    )

    if patient is None:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    return patient


@router.delete(
    "/{patient_id}"
)
def delete_patient(
    patient_id: int,
    db: Session = Depends(get_db)
):
    patient = service.delete_patient(
        db=db,
        patient_id=patient_id
    )

    if patient is None:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    return {
        "message": "Patient deleted successfully"
    }