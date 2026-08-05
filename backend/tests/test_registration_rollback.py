import os
from sqlalchemy import select
from sqlalchemy.orm import Session

from fastapi import status


def test_duplicate_registration_rolls_back(client, unique_email):
    payload = {
        "full_name": "Rollback Test",
        "email": unique_email,
        "password": "TestPass123!"
    }

    # First registration should succeed
    r1 = client.post("/auth/register", json=payload)
    assert r1.status_code == 201

    # Second registration with the same email should return 400
    r2 = client.post("/auth/register", json=payload)
    assert r2.status_code == 400
    body = r2.json()
    assert body.get("detail") == "Email is already registered"

    # Confirm the app is bound to the test database (safety check)
    from app.core import config as app_config
    assert os.environ.get("DATABASE_URL") == app_config.settings.DATABASE_URL

    # Verify only one user exists with that email in the isolated test DB
    from app.models.user import User
    from app.database.session import engine

    with Session(engine) as session:
        stmt = select(User).where(User.email == unique_email)
        rows = session.scalars(stmt).all()
        assert len(rows) == 1
