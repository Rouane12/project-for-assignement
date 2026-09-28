def test_create_guest_issue(client):
    response = client.post(
        "/api/reservations/1/guest-issues",
        json={
            "category": "access",
            "description": "The keypad code is being rejected.",
            "urgency": "high",
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["reservation_id"] == 1
    assert body["property_name"] == "Marina Loft"
    assert body["guest_name"] == "Maya Chen"
    assert body["category"] == "access"
    assert body["urgency"] == "high"
    assert body["status"] == "open"


def test_guest_issue_for_missing_reservation(client):
    response = client.post(
        "/api/reservations/999/guest-issues",
        json={
            "category": "noise",
            "description": "There is excessive noise outside.",
            "urgency": "normal",
        },
    )

    assert response.status_code == 404


def test_guest_issue_rejected_for_terminal_reservation(client):
    response = client.post(
        "/api/reservations/2/guest-issues",
        json={
            "category": "access",
            "description": "The guest cannot enter the property.",
            "urgency": "high",
        },
    )

    assert response.status_code == 409


def test_legal_reservation_status_transition(client):
    response = client.patch(
        "/api/reservations/1/status",
        json={
            "status": "checked_in",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "checked_in"


def test_illegal_reservation_status_transition(client):
    response = client.patch(
        "/api/reservations/2/status",
        json={
            "status": "checked_in",
        },
    )

    assert response.status_code == 409


def test_repeating_current_status_succeeds(client):
    response = client.patch(
        "/api/reservations/1/status",
        json={
            "status": "confirmed",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "confirmed"


def test_duplicate_scheduled_cleaning_task_returns_conflict(client):
    first_response = client.post(
        "/api/reservations/1/cleaning-tasks"
    )

    second_response = client.post(
        "/api/reservations/1/cleaning-tasks"
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409