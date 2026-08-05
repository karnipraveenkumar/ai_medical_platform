from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from fastapi import HTTPException, status

from app.api.patient.schemas import PatientCreate, PatientUpdate
from app.models.patient import Patient


def create_patient(
    db: Session,
    patient_data: PatientCreate,
) -> Patient:
    """Create a new patient record in the database."""
    # Pre-check for duplicate email to return a friendly 409
    if patient_data.email:
        existing = db.query(Patient).filter(Patient.email == patient_data.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A patient with this email already exists.",
            )

    new_patient = Patient(
        first_name=patient_data.first_name,
        last_name=patient_data.last_name,
        email=patient_data.email,
        phone=patient_data.phone,
        date_of_birth=patient_data.date_of_birth,
    )

    db.add(new_patient)
    try:
        db.commit()
        db.refresh(new_patient)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A patient with this email already exists.",
        )

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
    """Update an existing patient record with only provided fields."""
    patient = get_patient(db=db, patient_id=patient_id)

    if patient is None:
        return None

    # Update only provided fields (partial update)
    if patient_data.first_name is not None:
        patient.first_name = patient_data.first_name
    if patient_data.last_name is not None:
        patient.last_name = patient_data.last_name
    if patient_data.email is not None:
        # Check duplicate email
        existing = db.query(Patient).filter(Patient.email == patient_data.email, Patient.id != patient_id).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A patient with this email already exists.",
            )
        patient.email = patient_data.email
    if patient_data.phone is not None:
        patient.phone = patient_data.phone
    if patient_data.date_of_birth is not None:
        patient.date_of_birth = patient_data.date_of_birth

    try:
        db.commit()
        db.refresh(patient)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A patient with this email already exists.",
        )

    return patient


def delete_patient(db: Session, patient_id: int) -> Patient | None:
    """Delete a patient record from the database."""
    patient = get_patient(db=db, patient_id=patient_id)

    if patient is None:
        return None

    db.delete(patient)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise

    return patient
