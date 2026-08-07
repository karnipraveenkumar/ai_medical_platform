from datetime import datetime, date

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        index=True,
        nullable=False,
    )

    phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    # ✅ FIXED
    date_of_birth: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    age: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    gender: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    phone_number: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    address: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    user = relationship(
        "User",
        back_populates="patients",
    )

    medical_records = relationship(
        "MedicalRecord",
        back_populates="patient",
        cascade="all, delete-orphan",
    )