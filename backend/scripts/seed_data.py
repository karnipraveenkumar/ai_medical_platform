"""
Seed script to add sample users and patients to the PostgreSQL database.

Usage (run from the backend folder):
  python scripts/seed_data.py

This script is idempotent: it checks existing records and skips duplicates.
It uses the project's SQLAlchemy session configuration and the password
hashing helper at `app.auth.password.hash_password`.
"""
from datetime import date

from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.models.user import User
from app.models.patient import Patient
from app.auth.password import hash_password


def split_name(full_name: str) -> tuple[str, str]:
    parts = full_name.strip().split()
    if len(parts) == 0:
        return "", ""
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], " ".join(parts[1:])


def approximate_date_of_birth(age: int) -> date:
    today = date.today()
    year = today.year - age
    try:
        return date(year, today.month, today.day)
    except ValueError:
        return date(year, 1, 1)


USERS = [
    {"full_name": "Alice Carter", "email": "alice.carter+dev1@example.com", "password": "TestPass123!"},
    {"full_name": "Benjamin Torres", "email": "ben.torres+dev2@example.com", "password": "TestPass123!"},
    {"full_name": "Carla Nguyen", "email": "carla.nguyen+dev3@example.com", "password": "TestPass123!"},
    {"full_name": "Daniel Okafor", "email": "daniel.okafor+dev4@example.com", "password": "TestPass123!"},
    {"full_name": "Elena Petrova", "email": "elena.petrova+dev5@example.com", "password": "TestPass123!"},
    {"full_name": "Faris Haddad", "email": "faris.haddad+dev6@example.com", "password": "TestPass123!"},
    {"full_name": "Grace Lee", "email": "grace.lee+dev7@example.com", "password": "TestPass123!"},
    {"full_name": "Hector Morales", "email": "hector.morales+dev8@example.com", "password": "TestPass123!"},
    {"full_name": "Isha Kapoor", "email": "isha.kapoor+dev9@example.com", "password": "TestPass123!"},
    {"full_name": "Jonah Smith", "email": "jonah.smith+dev10@example.com", "password": "TestPass123!"},
]

PATIENTS = [
    {"name": "Sam Johnson", "age": 34, "gender": "male", "phone": "+1-555-0100", "email": "sam.johnson+pt1@example.com", "medical_history": "No known allergies; previous appendectomy."},
    {"name": "Maya Patel", "age": 28, "gender": "female", "phone": "+1-555-0101", "email": "maya.patel+pt2@example.com", "medical_history": "Asthma since childhood."},
    {"name": "Liam O'Neill", "age": 45, "gender": "male", "phone": "+1-555-0102", "email": "liam.oneill+pt3@example.com", "medical_history": "Type 2 diabetes."},
    {"name": "Olivia Brown", "age": 52, "gender": "female", "phone": "+1-555-0103", "email": "olivia.brown+pt4@example.com", "medical_history": "Hypertension; on medication."},
    {"name": "Noah Wilson", "age": 60, "gender": "male", "phone": "+1-555-0104", "email": "noah.wilson+pt5@example.com", "medical_history": "History of myocardial infarction."},
    {"name": "Emma Davis", "age": 19, "gender": "female", "phone": "+1-555-0105", "email": "emma.davis+pt6@example.com", "medical_history": "Seasonal allergies."},
    {"name": "Oliver Zhang", "age": 37, "gender": "male", "phone": "+1-555-0106", "email": "oliver.zhang+pt7@example.com", "medical_history": "No chronic conditions reported."},
    {"name": "Ava Rossi", "age": 29, "gender": "female", "phone": "+1-555-0107", "email": "ava.rossi+pt8@example.com", "medical_history": "Iron-deficiency anemia."},
    {"name": "Lucas Martins", "age": 41, "gender": "male", "phone": "+1-555-0108", "email": "lucas.martins+pt9@example.com", "medical_history": "Knee surgery in 2018."},
    {"name": "Sofia Garcia", "age": 33, "gender": "female", "phone": "+1-555-0109", "email": "sofia.garcia+pt10@example.com", "medical_history": "Pregnancy history: 1 birth."},
]


def seed():
    added_users = 0
    skipped_users = 0
    added_patients = 0
    skipped_patients = 0
    session: Session = SessionLocal()
    total_users = 0
    total_patients = 0
    try:
        # Seed users
        for u in USERS:
            existing = session.query(User).filter_by(email=u["email"]).first()
            if existing:
                skipped_users += 1
                continue

            hashed = hash_password(u["password"])
            user = User(
                full_name=u["full_name"],
                email=u["email"],
                hashed_password=hashed,
                is_active=True,
            )
            session.add(user)
            added_users += 1

        # Seed patients
        for p in PATIENTS:
            first_name, last_name = split_name(p["name"])
            existing_patient = None
            if p.get("email"):
                existing_patient = session.query(Patient).filter_by(email=p["email"]).first()

            if not existing_patient:
                existing_patient = session.query(Patient).filter_by(
                    first_name=first_name,
                    last_name=last_name,
                    phone=p.get("phone"),
                ).first()

            if existing_patient:
                skipped_patients += 1
                continue

            patient = Patient(
                first_name=first_name,
                last_name=last_name,
                email=p.get("email"),
                phone=p.get("phone"),
                date_of_birth=approximate_date_of_birth(p["age"]),
            )
            session.add(patient)
            added_patients += 1

        # Commit once after adding all records
        session.commit()

        # Totals after commit
        total_users = session.query(User).count()
        total_patients = session.query(Patient).count()

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()

    # Print exactly the requested messages
    print(f"New users added: {added_users}")
    print(f"New patients added: {added_patients}")
    print(f"Existing users skipped: {skipped_users}")
    print(f"Existing patients skipped: {skipped_patients}")
    print(f"Total users in database: {total_users}")
    print(f"Total patients in database: {total_patients}")
    print("Sample data inserted successfully.")


if __name__ == "__main__":
    seed()
