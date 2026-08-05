from sqlalchemy.orm import Session

from app.api.patient.schemas import PatientCreate, PatientUpdate
from app.models.patient import Patient


def create_patient(
    db: Session,
    patient_data: PatientCreate,
) -> Patient:
    """Create a new patient record in the database."""
    new_patient = Patient(
        name=patient_data.name,
        age=patient_data.age,
        gender=patient_data.gender,
        phone=patient_data.phone,
        email=patient_data.email,
        medical_history=patient_data.medical_history,
    )

    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)

    return new_patient


def get_patients(db: Session) -> list[Patient]:
    """Return all patients from the database."""
    return db.query(Patient).all()


def get_patient(db: Session, patient_id: int) -> Patient | None:
    """Return a patient by ID."""
    return db.query(Patient).filter(Patient.id == patient_id).first()


def update_patient(
    db: Session,
    patient_id: int,
    patient_data: PatientUpdate,
) -> Patient | None:
    """Update an existing patient record."""
    patient = get_patient(db=db, patient_id=patient_id)

    if patient is None:
        return None

    patient.name = patient_data.name
    patient.age = patient_data.age
    patient.gender = patient_data.gender
    patient.phone = patient_data.phone
    patient.email = patient_data.email
    patient.medical_history = patient_data.medical_history

    db.commit()
    db.refresh(patient)

    return patient


def delete_patient(db: Session, patient_id: int) -> Patient | None:
    """Delete a patient record from the database."""
    patient = get_patient(db=db, patient_id=patient_id)

    if patient is None:
        return None

    db.delete(patient)
    db.commit()

    return patient
