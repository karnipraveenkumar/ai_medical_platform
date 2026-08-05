from sqlalchemy.orm import Session

from app.api.doctor import repository
from app.api.doctor.schemas import DoctorCreate, DoctorUpdate


def create_doctor(db: Session, doctor_data: DoctorCreate):
    return repository.create_doctor(db=db, doctor_data=doctor_data)


def get_doctors(db: Session):
    return repository.get_doctors(db=db)


def get_doctor(db: Session, doctor_id: int):
    return repository.get_doctor(db=db, doctor_id=doctor_id)


def update_doctor(db: Session, doctor_id: int, doctor_data: DoctorUpdate):
    return repository.update_doctor(db=db, doctor_id=doctor_id, doctor_data=doctor_data)


def delete_doctor(db: Session, doctor_id: int):
    return repository.delete_doctor(db=db, doctor_id=doctor_id)
