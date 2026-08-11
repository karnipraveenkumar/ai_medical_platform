from sqlalchemy.orm import Session

from repositories import patient_repository


def create_patient(db: Session, patient_data):
    return patient_repository.create_patient(db=db, patient_data=patient_data)


def get_patients(db: Session):
    return get_patients(db=db)


def get_patient(db: Session, patient_id: int):
    return get_patient(db=db, patient_id=patient_id)


def update_patient(db: Session, patient_id: int, patient_data):
    return update_patient(
        db=db,
        patient_id=patient_id,
        patient_data=patient_data,
    )


def delete_patient(db: Session, patient_id: int):
    return delete_patient(db=db, patient_id=patient_id)
