from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.auth.dependencies import get_current_user
from app.api.patient.schemas import (
    PatientCreate,
    PatientResponse,
    PatientUpdate,
)
from app.api.patient import service
from app.database.session import get_db
from app.models.user import User


router = APIRouter(
    prefix="/patients",
    tags=["Patients"]
)


@router.post(
    "/",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_patient(
    patient: PatientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.create_patient(
        db=db,
        patient_data=patient,
        owner_id=current_user.id,
    )

@router.get(
    "/",
    response_model=list[PatientResponse],
)
def get_patients(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.get_patients(db=db, owner_id=current_user.id)


@router.get(
    "/{patient_id}",
    response_model=PatientResponse,
)
def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    patient = service.get_patient(
        db=db, patient_id=patient_id, owner_id=current_user.id
    )

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    return patient


@router.put(
    "/{patient_id}",
    response_model=PatientResponse,
)
def update_patient(
    patient_id: int,
    patient_data: PatientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    patient = service.update_patient(
        db=db,
        patient_id=patient_id,
        patient_data=patient_data,
        owner_id=current_user.id,
    )

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    return patient


@router.delete(
    "/{patient_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    patient = service.delete_patient(
        db=db,
        patient_id=patient_id,
        owner_id=current_user.id,
    )

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    return None