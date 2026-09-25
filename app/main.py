from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import select

from app import models
from app.database import Base, SessionLocal, engine
from app.routes import reservations, webhooks


def seed_data() -> None:
    with SessionLocal() as db:
        existing = db.scalar(select(models.Reservation).limit(1))
        if existing is not None:
            return

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


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed_data()
    yield


app = FastAPI(
    title="StayOps Practice API",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(reservations.router)
app.include_router(webhooks.router)


@app.get("/health")
def health():
    return {"status": "ok"}
