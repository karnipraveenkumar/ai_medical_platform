from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.api.patient.schemas import (
    PatientCreate,
    PatientResponse
)
from app.api.patient import service


router = APIRouter(
    prefix="/patients",
    tags=["Patients"]
)


@router.post(
    "/",
    response_model=PatientResponse
)
def create_patient(
    patient: PatientCreate,
    db: Session = Depends(get_db)
):

    return service.create_patient(
        db,
        patient
    )


@router.get(
    "/",
    response_model=list[PatientResponse]
)
def get_patients(
    db: Session = Depends(get_db)
):

    return service.get_patients(db)


@router.get(
    "/{patient_id}",
    response_model=PatientResponse
)
def get_patient(
    patient_id: int,
    db: Session = Depends(get_db)
):

    return service.get_patient_by_id(
        db,
        patient_id
    )


@router.delete(
    "/{patient_id}"
)
def delete_patient(
    patient_id: int,
    db: Session = Depends(get_db)
):

    service.delete_patient(
        db,
        patient_id
    )

    return {
        "message": "Patient deleted successfully"
    }
