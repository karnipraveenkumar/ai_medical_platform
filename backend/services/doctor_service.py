from sqlalchemy.orm import Session

from repositories import doctor_repository


def create_doctor(db: Session, doctor_data):
    return doctor_repository.create_doctor(db=db, doctor_data=doctor_data)


def get_doctors(db: Session):
    return get_doctors(db=db)


def get_doctor(db: Session, doctor_id: int):
    return get_doctor(db=db, doctor_id=doctor_id)


def update_doctor(db: Session, doctor_id: int, doctor_data):
    return update_doctor(
        db=db,
        doctor_id=doctor_id,
        doctor_data=doctor_data,
    )


def delete_doctor(db: Session, doctor_id: int):
    return delete_doctor(db=db, doctor_id=doctor_id)
