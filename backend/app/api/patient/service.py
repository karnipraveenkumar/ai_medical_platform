from sqlalchemy.orm import Session

from app.api.patient import repository
from app.api.patient.schemas import PatientCreate, PatientUpdate


def create_patient(
    db: Session,
    patient_data: PatientCreate,
    owner_id: int,
):
    return repository.create_patient(
        db=db,
        patient_data=patient_data,
        owner_id=owner_id,
    )


def get_patients(
    db: Session,
    owner_id: int,
):
    return repository.get_patients(
        db=db,
        owner_id=owner_id,
    )


def get_patient(
    db: Session,
    patient_id: int,
    owner_id: int,
):
    return repository.get_patient(
        db=db,
        patient_id=patient_id,
        owner_id=owner_id,
    )


def update_patient(
    db: Session,
    patient_id: int,
    patient_data: PatientUpdate,
    owner_id: int,
):
    return repository.update_patient(
        db=db,
        patient_id=patient_id,
        patient_data=patient_data,
        owner_id=owner_id,
    )


def delete_patient(
    db: Session,
    patient_id: int,
    owner_id: int,
):
    return repository.delete_patient(
        db=db,
        patient_id=patient_id,
        owner_id=owner_id,
    )