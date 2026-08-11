from sqlalchemy.orm import Session

from repositories import appointment_repository


def create_appointment(db: Session, appointment_data):
    return appointment_repository.create_appointment(db=db, appointment_data=appointment_data)


def get_appointments(db: Session):
    return get_appointments(db=db)


def get_appointment(db: Session, appointment_id: int):
    return get_appointment(db=db, appointment_id=appointment_id)


def update_appointment(db: Session, appointment_id: int, appointment_data):
    return update_appointment(
        db=db,
        appointment_id=appointment_id,
        appointment_data=appointment_data,
    )


def delete_appointment(db: Session, appointment_id: int):
    return delete_appointment(db=db, appointment_id=appointment_id)
