from sqlalchemy.orm import Session

from models.patient import Patient


def create_patient(db: Session, patient_data):
    patient = Patient(
        first_name=patient_data.first_name,
        last_name=patient_data.last_name,
        email=patient_data.email,
        phone=patient_data.phone,
        date_of_birth=patient_data.date_of_birth,
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


def get_patients(db: Session):
    return db.query(Patient).all()


def get_patient(db: Session, patient_id: int):
    return db.query(Patient).filter(Patient.id == patient_id).first()


def update_patient(db: Session, patient_id: int, patient_data):
    patient = get_patient(db=db, patient_id=patient_id)
    if patient is None:
        return None

    patient.first_name = patient_data.first_name
    patient.last_name = patient_data.last_name
    patient.email = patient_data.email
    patient.phone = patient_data.phone
    patient.date_of_birth = patient_data.date_of_birth

    db.commit()
    db.refresh(patient)
    return patient


def delete_patient(db: Session, patient_id: int):
    patient = get_patient(db=db, patient_id=patient_id)
    if patient is None:
        return None

    db.delete(patient)
    db.commit()
    return patient
