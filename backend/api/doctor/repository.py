from sqlalchemy.orm import Session

from app.models.doctor import Doctor
from app.api.doctor.schemas import DoctorCreate, DoctorUpdate


def create_doctor(db: Session, doctor_data: DoctorCreate) -> Doctor:
    doc = Doctor(
        full_name=doctor_data.full_name,
        specialty=doctor_data.specialty,
        email=doctor_data.email,
        phone=doctor_data.phone,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def get_doctors(db: Session) -> list[Doctor]:
    return db.query(Doctor).all()


def get_doctor(db: Session, doctor_id: int) -> Doctor | None:
    return db.query(Doctor).filter(Doctor.id == doctor_id).first()


def update_doctor(db: Session, doctor_id: int, doctor_data: DoctorUpdate) -> Doctor | None:
    doc = get_doctor(db=db, doctor_id=doctor_id)
    if doc is None:
        return None

    doc.full_name = doctor_data.full_name
    doc.specialty = doctor_data.specialty
    doc.phone = doctor_data.phone

    db.commit()
    db.refresh(doc)
    return doc


def delete_doctor(db: Session, doctor_id: int) -> Doctor | None:
    doc = get_doctor(db=db, doctor_id=doctor_id)
    if doc is None:
        return None

    db.delete(doc)
    db.commit()
    return doc
