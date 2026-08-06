from app.database.base import Base
from app.database.database import engine

# Import all models so SQLAlchemy registers them before create_all()
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.user import User


Base.metadata.create_all(
    bind=engine
)

print("User, patient, and doctor tables created successfully!")