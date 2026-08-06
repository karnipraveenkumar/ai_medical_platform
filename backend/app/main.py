from fastapi import FastAPI

from app.database.base import Base
from app.database.database import engine
from app.models.doctor import Doctor
from app.models.medical_record import MedicalRecord
from app.models.patient import Patient
from app.models.user import User
from app.api.ai.routes import router as ai_router
from app.api.doctor.routes import router as doctor_router
from app.api.patient.routes import router as patient_router
from app.api.auth.routes import router as auth_router
from app.api.doctor.routes import router as doctor_router
from app.api.ai.routes import router as ai_router


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="AI Medical Platform API",
    version="1.0.0",
    description="AI-powered medical platform backend",
)


@app.get("/")
def root():
    return {
        "message": "AI Medical Platform API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


app.include_router(
    patient_router
)

app.include_router(
    auth_router
)

app.include_router(
    doctor_router
)

app.include_router(
    ai_router
)