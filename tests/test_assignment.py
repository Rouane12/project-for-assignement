def test_create_maintenance_request(client):
    response = client.post(
        "/api/reservations/1/maintenance-requests",
        json={
            "issue_type": "heating",
            "description": "The bedroom radiator is not warming up.",
            "severity": "medium",
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["reservation_id"] == 1
    assert body["property_name"] == "Marina Loft"
    assert body["issue_type"] == "heating"
    assert body["description"] == "The bedroom radiator is not warming up."
    assert body["severity"] == "medium"
    assert body["status"] == "open"


def test_maintenance_request_for_missing_reservation(client):
    response = client.post(
        "/api/reservations/999/maintenance-requests",
        json={
            "issue_type": "plumbing",
            "description": "The bathroom sink is leaking.",
            "severity": "high",
        },
    )

    assert response.status_code == 404


def test_maintenance_request_for_cancelled_reservation(client):
    response = client.post(
        "/api/reservations/2/maintenance-requests",
        json={
            "issue_type": "access",
            "description": "The guest cannot open the front door.",
            "severity": "high",
        },
    )

    assert response.status_code == 409


def test_cleaning_task_rejected_for_cancelled_reservation(client):
    response = client.post(
        "/api/reservations/2/cleaning-tasks"
    )

    assert response.status_code == 409


def test_duplicate_payment_webhook_does_not_repeat_notification(client):
    payload = {
        "event_id": "evt_duplicate_test",
        "reservation_id": 1,
        "status": "paid",
    }

    first_response = client.post(
        "/api/webhooks/payments",
        json=payload,
    )

    second_response = client.post(
        "/api/webhooks/payments",
        json=payload,
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    first_body = first_response.json()
    second_body = second_response.json()

    assert first_body["duplicate"] is False
    assert first_body["payment_notifications_sent"] == 1

    assert second_body["duplicate"] is True
    assert second_body["payment_notifications_sent"] == 1