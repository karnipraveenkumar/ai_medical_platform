from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.auth.schemas import (
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)
from app.api.auth.service import (
    login_user,
    register_user,
)
from app.database.session import get_db


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    return register_user(
        db=db,
        user_data=user_data
    )


@router.post(
    "/login",
    response_model=TokenResponse
)
def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    access_token = login_user(
        db=db,
        login_data=login_data
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
