from sqlalchemy.orm import Session

from app.api.patient import repository
from app.api.patient.schemas import PatientCreate, PatientUpdate


def create_patient(
    db: Session,
    patient_data: PatientCreate
):
    return repository.create_patient(
        db=db,
        patient_data=patient_data
    )


def get_patients(
    db: Session
):
    return repository.get_patients(
        db=db
    )


def get_patient(
    db: Session,
    patient_id: int
):
    return repository.get_patient(
        db=db,
        patient_id=patient_id
    )


def update_patient(
    db: Session,
    patient_id: int,
    patient_data: PatientUpdate
):
    return repository.update_patient(
        db=db,
        patient_id=patient_id,
        patient_data=patient_data
    )


def delete_patient(
    db: Session,
    patient_id: int
):
    return repository.delete_patient(
        db=db,
        patient_id=patient_id
    )
