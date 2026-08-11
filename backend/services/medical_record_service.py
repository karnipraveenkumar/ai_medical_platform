from sqlalchemy.orm import Session

from repositories import medical_record_repository


def create_medical_record(db: Session, medical_record_data):
    return medical_record_repository.create_medical_record(
        db=db,
        medical_record_data=medical_record_data,
    )


def get_medical_records(db: Session):
    return get_medical_records(db=db)


def get_medical_record(db: Session, medical_record_id: int):
    return get_medical_record(
        db=db,
        medical_record_id=medical_record_id,
    )


def update_medical_record(db: Session, medical_record_id: int, medical_record_data):
    return update_medical_record(
        db=db,
        medical_record_id=medical_record_id,
        medical_record_data=medical_record_data,
    )


def delete_medical_record(db: Session, medical_record_id: int):
    return delete_medical_record(
        db=db,
        medical_record_id=medical_record_id,
    )
