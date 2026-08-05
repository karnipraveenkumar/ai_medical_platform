from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.models.user import User


def get_user_by_email(
    db: Session,
    email: str
) -> User | None:
    statement = select(User).where(User.email == email)
    return db.scalar(statement)


def get_user_by_id(
    db: Session,
    user_id: int,
) -> User | None:
    statement = select(User).where(User.id == user_id)
    return db.scalar(statement)


def create_user(
    db: Session,
    full_name: str,
    email: str,
    hashed_password: str,
) -> User:
    user = User(
        full_name=full_name,
        email=email,
        hashed_password=hashed_password,
    )
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
        return user
    except IntegrityError:
        # Ensure the session is clean for the caller and raise a
        # controlled HTTP error matching the existing duplicate-email
        # behavior used elsewhere in the codebase.
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered",
        )
