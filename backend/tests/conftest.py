import os
import tempfile
from pathlib import Path
import uuid

import pytest

# Set up a test database before importing the app so production DB is not used.
# Use a file-based sqlite db in a temp directory to avoid in-memory connection scope issues.
TEST_DB_DIR = Path(tempfile.gettempdir()) / f"ai_medical_tests_{uuid.uuid4().hex}"
TEST_DB_DIR.mkdir(parents=True, exist_ok=True)
TEST_DB_PATH = TEST_DB_DIR / "test.db"

os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"

from fastapi.testclient import TestClient

# Import app after DATABASE_URL is set so app.database.session binds to test DB
from app.main import app
from app.database.session import engine
from app.database.base import Base


# Create tables for tests
Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def unique_email():
    return f"test+{uuid.uuid4().hex}@example.com"


@pytest.fixture
def new_user_payload(unique_email):
    return {
        "full_name": "Test User",
        "email": unique_email,
        "password": "TestPass123!"
    }


@pytest.fixture
def auth_headers(client: TestClient, new_user_payload):
    # register then login to obtain a bearer token
    resp = client.post("/auth/register", json=new_user_payload)
    assert resp.status_code in (200, 201)
    data = {"username": new_user_payload["email"], "password": new_user_payload["password"]}
    login = client.post("/auth/login", data=data)
    assert login.status_code == 200
    token = login.json().get("access_token")
    return {"Authorization": f"Bearer {token}"}
