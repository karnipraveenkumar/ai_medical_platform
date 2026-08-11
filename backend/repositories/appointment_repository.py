from sqlalchemy.orm import Session

from models.appointment import Appointment


def create_appointment(db: Session, appointment_data):
    appointment = Appointment(
        patient_id=appointment_data.patient_id,
        doctor_id=appointment_data.doctor_id,
        start_time=appointment_data.start_time,
        end_time=appointment_data.end_time,
        reason=appointment_data.reason,
        is_confirmed=getattr(appointment_data, "is_confirmed", False),
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment


def get_appointments(db: Session):
    return db.query(Appointment).all()


def get_appointment(db: Session, appointment_id: int):
    return db.query(Appointment).filter(Appointment.id == appointment_id).first()


def update_appointment(db: Session, appointment_id: int, appointment_data):
    appointment = get_appointment(db=db, appointment_id=appointment_id)
    if appointment is None:
        return None

    appointment.patient_id = appointment_data.patient_id
    appointment.doctor_id = appointment_data.doctor_id
    appointment.start_time = appointment_data.start_time
    appointment.end_time = appointment_data.end_time
    appointment.reason = appointment_data.reason
    appointment.is_confirmed = appointment_data.is_confirmed

    db.commit()
    db.refresh(appointment)
    return appointment


def delete_appointment(db: Session, appointment_id: int):
    appointment = get_appointment(db=db, appointment_id=appointment_id)
    if appointment is None:
        return None

    db.delete(appointment)
    db.commit()
    return appointment
