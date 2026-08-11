from sqlalchemy.orm import Session

from repositories import billing_repository


def create_billing(db: Session, billing_data):
    return billing_repository.create_billing(db=db, billing_data=billing_data)


def get_billings(db: Session):
    return get_billings(db=db)


def get_billing(db: Session, billing_id: int):
    return get_billing(db=db, billing_id=billing_id)


def update_billing(db: Session, billing_id: int, billing_data):
    return update_billing(
        db=db,
        billing_id=billing_id,
        billing_data=billing_data,
    )


def delete_billing(db: Session, billing_id: int):
    return delete_billing(db=db, billing_id=billing_id)
