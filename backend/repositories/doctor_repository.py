from sqlalchemy.orm import Session

from app.models.doctor import Doctor


def create_doctor(db: Session, doctor_data):
    doctor = Doctor(
        full_name=doctor_data.full_name,
        specialty=doctor_data.specialty,
        email=doctor_data.email,
        phone=doctor_data.phone,
    )
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor


def get_doctors(db: Session):
    return db.query(Doctor).all()


def get_doctor(db: Session, doctor_id: int):
    return db.query(Doctor).filter(Doctor.id == doctor_id).first()


def update_doctor(db: Session, doctor_id: int, doctor_data):
    doctor = get_doctor(db=db, doctor_id=doctor_id)
    if doctor is None:
        return None

    doctor.full_name = doctor_data.full_name
    doctor.specialty = doctor_data.specialty
    doctor.phone = doctor_data.phone

    db.commit()
    db.refresh(doctor)
    return doctor


def delete_doctor(db: Session, doctor_id: int):
    doctor = get_doctor(db=db, doctor_id=doctor_id)
    if doctor is None:
        return None

    db.delete(doctor)
    db.commit()
    return doctor
