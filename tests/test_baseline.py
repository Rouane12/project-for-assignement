def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_existing_reservation(client):
    response = client.get("/api/reservations/1")

    assert response.status_code == 200
    assert response.json()["guest_name"] == "Maya Chen"
    assert response.json()["property_name"] == "Marina Loft"


def test_get_missing_reservation(client):
    response = client.get("/api/reservations/999")

    assert response.status_code == 404


def test_create_cleaning_task_for_confirmed_reservation(client):
    response = client.post("/api/reservations/1/cleaning-tasks")

    assert response.status_code == 201
    assert response.json()["reservation_id"] == 1
    assert response.json()["status"] == "scheduled"


def test_payment_webhook_updates_payment_status(client):
    response = client.post(
        "/api/webhooks/payments",
        json={
            "event_id": "evt_baseline",
            "reservation_id": 1,
            "status": "paid",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["payment_status"] == "paid"
    assert body["payment_notifications_sent"] == 1
    assert body["duplicate"] is False
