def test_doctor_creation(client):
    payload = {
        "full_name": "Dr. Ada",
        "specialty": "Cardiology",
        "email": "ada.doctor@example.com",
        "phone": "555-0101",
    }

    response = client.post("/doctors/", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["full_name"] == payload["full_name"]
    assert body["specialty"] == payload["specialty"]
