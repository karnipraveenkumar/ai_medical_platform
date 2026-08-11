from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class User(Base):

    __tablename__ = "users"


    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )


    email: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        nullable=False,
        index=True
    )


    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )


    role: Mapped[str] = mapped_column(
        String(50),
        default="patient",
        nullable=False
    )


    full_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )


    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )


    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )


    doctor = relationship(
        "Doctor",
        back_populates="user",
        uselist=False
    )


    patient = relationship(
        "Patient",
        back_populates="user",
        uselist=False
    )