import os

import pytest
from fastapi.testclient import TestClient

from app import models
from app.database import Base, SessionLocal, engine
from app.main import app


@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        db.add_all(
            [
                models.Reservation(
                    id=1,
                    guest_name="Maya Chen",
                    property_name="Marina Loft",
                    status="confirmed",
                    payment_status="pending",
                ),
                models.Reservation(
                    id=2,
                    guest_name="Omar Haddad",
                    property_name="Old Town Studio",
                    status="cancelled",
                    payment_status="pending",
                ),
                models.Reservation(
                    id=3,
                    guest_name="Sofia Martins",
                    property_name="Riverside Flat",
                    status="confirmed",
                    payment_status="paid",
                    payment_notifications_sent=1,
                ),
            ]
        )
        db.commit()

    yield

    Base.metadata.drop_all(bind=engine)

    if os.path.exists("practice.db"):
        try:
            os.remove("practice.db")
        except PermissionError:
            pass


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
