from datetime import datetime, date

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Prescription(Base):
    __tablename__ = "prescriptions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    patient_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("patients.id"),
        nullable=False,
    )

    doctor_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("doctors.id"),
        nullable=True,
    )

    medication_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    dosage: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    frequency: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    instructions: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    start_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    end_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
