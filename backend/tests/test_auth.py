import pytest


def test_register_and_duplicate(client, unique_email):
    payload = {
        "full_name": "Alice Test",
        "email": unique_email,
        "password": "TestPass123!"
    }

    # Register first time
    r = client.post("/auth/register", json=payload)
    assert r.status_code == 201
    body = r.json()
    assert body["email"] == unique_email

    # Register duplicate
    r2 = client.post("/auth/register", json=payload)
    assert r2.status_code == 400


def test_login_success_and_failure(client, unique_email):
    payload = {
        "full_name": "Bob Test",
        "email": unique_email,
        "password": "TestPass123!"
    }

    r = client.post("/auth/register", json=payload)
    assert r.status_code == 201

    # Successful login (OAuth2 form)
    data = {"username": unique_email, "password": payload["password"]}
    login = client.post("/auth/login", data=data)
    assert login.status_code == 200
    token = login.json().get("access_token")
    assert token

    # Invalid password
    bad = client.post("/auth/login", data={"username": unique_email, "password": "wrong"})
    assert bad.status_code == 401

    # Non-existent email
    fake = client.post("/auth/login", data={"username": "noone@example.com", "password": "x"})
    assert fake.status_code == 401
