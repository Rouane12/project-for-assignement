from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories import ReservationRepository, WebhookRepository
from app.schemas import PaymentWebhookEvent, PaymentWebhookResult
from app.services import PaymentWebhookService, ReservationNotFoundError


router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])


@router.post("/payments", response_model=PaymentWebhookResult)
def process_payment_webhook(
    payload: PaymentWebhookEvent,
    db: Session = Depends(get_db),
):
    service = PaymentWebhookService(
        reservations=ReservationRepository(db),
        webhooks=WebhookRepository(db),
    )

    try:
        return service.process(payload)
    except ReservationNotFoundError:
        raise HTTPException(status_code=404, detail="Reservation not found")
