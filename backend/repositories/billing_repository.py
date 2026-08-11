from sqlalchemy.orm import Session

from models.billing import Billing


def create_billing(db: Session, billing_data):
    billing = Billing(
        patient_id=billing_data.patient_id,
        appointment_id=billing_data.appointment_id,
        amount=billing_data.amount,
        status=billing_data.status,
        due_date=billing_data.due_date,
        paid_date=billing_data.paid_date,
        description=billing_data.description,
        is_paid=billing_data.is_paid,
    )
    db.add(billing)
    db.commit()
    db.refresh(billing)
    return billing


def get_billings(db: Session):
    return db.query(Billing).all()


def get_billing(db: Session, billing_id: int):
    return db.query(Billing).filter(Billing.id == billing_id).first()


def update_billing(db: Session, billing_id: int, billing_data):
    billing = get_billing(db=db, billing_id=billing_id)
    if billing is None:
        return None

    billing.patient_id = billing_data.patient_id
    billing.appointment_id = billing_data.appointment_id
    billing.amount = billing_data.amount
    billing.status = billing_data.status
    billing.due_date = billing_data.due_date
    billing.paid_date = billing_data.paid_date
    billing.description = billing_data.description
    billing.is_paid = billing_data.is_paid

    db.commit()
    db.refresh(billing)
    return billing


def delete_billing(db: Session, billing_id: int):
    billing = get_billing(db=db, billing_id=billing_id)
    if billing is None:
        return None

    db.delete(billing)
    db.commit()
    return billing
