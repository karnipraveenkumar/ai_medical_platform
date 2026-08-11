import pytest
from uuid import uuid4


def sample_patient_payload(name_suffix="1"):
    return {
        "first_name": f"Test{ name_suffix }",
        "last_name": "Patient",
        "email": f"patient+{uuid4().hex}@example.com",
        "phone": "555-0100",
        "date_of_birth": "1990-01-01",
    }


def test_protected_without_token(client):
    r = client.get("/patients/")
    assert r.status_code == 401


def test_protected_with_token(client, auth_headers):
    r = client.get("/patients/", headers=auth_headers)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_patient_crud_flow(client, auth_headers):
    payload = sample_patient_payload()

    # Create
    r = client.post("/patients/", json=payload, headers=auth_headers)
    assert r.status_code == 201
    created = r.json()
    pid = created["id"]
    assert created["first_name"] == payload["first_name"]

    # Get all
    r2 = client.get("/patients/", headers=auth_headers)
    assert r2.status_code == 200
    assert any(p["id"] == pid for p in r2.json())

    # Get single
    r3 = client.get(f"/patients/{pid}", headers=auth_headers)
    assert r3.status_code == 200
    assert r3.json()["id"] == pid

    # Update
    upd = {"phone": "999-9999"}
    r4 = client.put(f"/patients/{pid}", json=upd, headers=auth_headers)
    assert r4.status_code == 200
    assert r4.json()["phone"] == upd["phone"]

    # Delete
    r5 = client.delete(f"/patients/{pid}", headers=auth_headers)
    assert r5.status_code == 204

    # Confirm deleted
    r6 = client.get(f"/patients/{pid}", headers=auth_headers)
    assert r6.status_code == 404
