from sqlalchemy.orm import Session

from app.api.appointments import repository


def create_appointment(db: Session, appointment_data):
    return repository.create_appointment(db=db, appointment_data=appointment_data)


def get_appointments(db: Session):
    return repository.get_appointments(db=db)


def get_appointment(db: Session, appointment_id: int):
    return repository.get_appointment(db=db, appointment_id=appointment_id)


def update_appointment(db: Session, appointment_id: int, appointment_data):
    return repository.update_appointment(
        db=db,
        appointment_id=appointment_id,
        appointment_data=appointment_data,
    )


def delete_appointment(db: Session, appointment_id: int):
    return repository.delete_appointment(db=db, appointment_id=appointment_id)
