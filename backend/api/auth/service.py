from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.api.auth.repository import (
    create_user,
    get_user_by_email,
)
from app.api.auth.schemas import (
    UserLogin,
    UserRegister,
)
from app.auth.jwt_handler import create_access_token
from app.auth.password import (
    hash_password,
    verify_password,
)
from app.models.user import User


def register_user(
    db: Session,
    user_data: UserRegister
) -> User:
    existing_user = get_user_by_email(
        db,
        user_data.email
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered"
        )

    hashed_password = hash_password(
        user_data.password
    )

    return create_user(
        db=db,
        full_name=user_data.full_name,
        email=user_data.email,
        hashed_password=hashed_password
    )


def login_user(
    db: Session,
    login_data: UserLogin
) -> str:
    user = get_user_by_email(
        db,
        login_data.email
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    password_is_valid = verify_password(
        login_data.password,
        user.hashed_password
    )

    if not password_is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    return create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email
        }
    )