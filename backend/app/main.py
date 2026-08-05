from fastapi import FastAPI

from app.database.base import Base
from app.database.session import engine
from app.models.patient import Patient
from app.api.patient.routes import router as patient_router


Base.metadata.create_all(
    bind=engine
)


app = FastAPI(
    title="AI Medical Platform API",
    version="1.0.0",
    description="AI-powered medical platform backend"
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