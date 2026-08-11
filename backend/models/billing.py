from datetime import datetime, date

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Billing(Base):
    __tablename__ = "billings"

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

    appointment_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("appointments.id"),
        nullable=True,
    )

    amount: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending",
    )

    due_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    paid_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    is_paid: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
