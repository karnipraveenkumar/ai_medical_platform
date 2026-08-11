from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.base import Base
from app.database.session import engine
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.user import User
from app.api.patient.routes import router as patient_router
from app.api.auth.routes import router as auth_router


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="AI Medical Platform API",
    version="1.0.0",
    description="Backend API for the AI Medical Platform"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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


app.include_router(patient_router)
app.include_router(auth_router)