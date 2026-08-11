from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class MedicalRecord(Base):
    __tablename__ = "medical_records"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    patient_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    doctor_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("doctors.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    symptoms: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    diagnosis: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    prescription: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(
        String(2000),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    patient = relationship("Patient", back_populates="medical_records")
    doctor = relationship("Doctor", back_populates="medical_records")
