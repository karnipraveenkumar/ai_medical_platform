from app.database.base import Base
from app.database.database import engine

# Import Patient so SQLAlchemy registers the model
from app.models.patient import Patient


Base.metadata.create_all(
    bind=engine
)

print("Patients table created successfully!")