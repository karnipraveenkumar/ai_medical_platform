from sqlalchemy.orm import Session

from app.api.doctor import schemas
from app.models.doctor import Doctor


def create_doctor(db: Session, doctor_data: schemas.DoctorCreate):

    new_doctor = Doctor(
        full_name=doctor_data.full_name,
        specialty=doctor_data.specialty,
        email=doctor_data.email,
        phone=doctor_data.phone,
    )

    db.add(new_doctor)
    db.commit()
    db.refresh(new_doctor)

    return new_doctor


def get_doctors(db: Session):
    return db.query(Doctor).all()


def get_doctor(db: Session, doctor_id: int):
    return db.query(Doctor).filter(
        Doctor.id == doctor_id
    ).first()


def update_doctor(
    db: Session,
    doctor_id: int,
    doctor_data: schemas.DoctorUpdate
):

    doctor = get_doctor(db, doctor_id)

    if doctor is None:
        return None

    data = doctor_data.model_dump(exclude_unset=True)

    for key, value in data.items():
        setattr(doctor, key, value)

    db.commit()
    db.refresh(doctor)

    return doctor


def delete_doctor(db: Session, doctor_id: int):

    doctor = get_doctor(db, doctor_id)

    if doctor is None:
        return None

    db.delete(doctor)
    db.commit()

    return doctor