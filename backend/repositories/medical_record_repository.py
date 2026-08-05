from sqlalchemy.orm import Session

from models.medical_record import MedicalRecord


def create_medical_record(db: Session, medical_record_data):
    record = MedicalRecord(
        patient_id=medical_record_data.patient_id,
        doctor_id=medical_record_data.doctor_id,
        record_type=medical_record_data.record_type,
        description=medical_record_data.description,
        record_date=medical_record_data.record_date,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_medical_records(db: Session):
    return db.query(MedicalRecord).all()


def get_medical_record(db: Session, medical_record_id: int):
    return db.query(MedicalRecord).filter(MedicalRecord.id == medical_record_id).first()


def update_medical_record(db: Session, medical_record_id: int, medical_record_data):
    record = get_medical_record(db=db, medical_record_id=medical_record_id)
    if record is None:
        return None

    record.patient_id = medical_record_data.patient_id
    record.doctor_id = medical_record_data.doctor_id
    record.record_type = medical_record_data.record_type
    record.description = medical_record_data.description
    record.record_date = medical_record_data.record_date

    db.commit()
    db.refresh(record)
    return record


def delete_medical_record(db: Session, medical_record_id: int):
    record = get_medical_record(db=db, medical_record_id=medical_record_id)
    if record is None:
        return None

    db.delete(record)
    db.commit()
    return record
