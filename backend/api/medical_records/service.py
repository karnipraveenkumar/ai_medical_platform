from sqlalchemy.orm import Session

from app.api.medical_records import repository


def create_medical_record(db: Session, medical_record_data):
    return repository.create_medical_record(
        db=db,
        medical_record_data=medical_record_data,
    )


def get_medical_records(db: Session):
    return repository.get_medical_records(db=db)


def get_medical_record(db: Session, medical_record_id: int):
    return repository.get_medical_record(db=db, medical_record_id=medical_record_id)


def update_medical_record(db: Session, medical_record_id: int, medical_record_data):
    return repository.update_medical_record(
        db=db,
        medical_record_id=medical_record_id,
        medical_record_data=medical_record_data,
    )


def delete_medical_record(db: Session, medical_record_id: int):
    return repository.delete_medical_record(db=db, medical_record_id=medical_record_id)
