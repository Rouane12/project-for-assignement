from dataclasses import dataclass

from app.repositories import (
    CleaningTaskRepository,
    ReservationRepository,
    WebhookRepository,
)
from app.schemas import PaymentWebhookEvent, ReservationStatus


class ReservationNotFoundError(Exception):
    pass


class InvalidReservationStateError(Exception):
    pass


@dataclass
class ReservationService:
    reservations: ReservationRepository

    def get(self, reservation_id: int):
        reservation = self.reservations.get(reservation_id)
        if reservation is None:
            raise ReservationNotFoundError
        return reservation

    def update_status(self, reservation_id: int, status: ReservationStatus):
        reservation = self.get(reservation_id)
        reservation.status = status.value
        return self.reservations.save(reservation)


@dataclass
class CleaningService:
    reservations: ReservationRepository
    cleaning_tasks: CleaningTaskRepository

    def create_task(self, reservation_id: int):
        # NOTE: This method currently contains a product bug described in ASSIGNMENT.md.
        reservation = self.reservations.get(reservation_id)
        if reservation is None:
            raise ReservationNotFoundError

        return self.cleaning_tasks.create(reservation_id)


@dataclass
class PaymentWebhookService:
    reservations: ReservationRepository
    webhooks: WebhookRepository

    def process(self, event: PaymentWebhookEvent):
        # NOTE: Payment providers may retry the same event.
        # The current implementation does not yet protect against duplicate processing.
        reservation = self.reservations.get(event.reservation_id)
        if reservation is None:
            raise ReservationNotFoundError

        reservation.payment_status = event.status.value

        if event.status.value == "paid":
            # Simulates a side effect such as sending a payment-confirmation notification.
            reservation.payment_notifications_sent += 1

        self.reservations.save(reservation)

        return {
            "event_id": event.event_id,
            "reservation_id": reservation.id,
            "payment_status": reservation.payment_status,
            "payment_notifications_sent": reservation.payment_notifications_sent,
            "duplicate": False,
        }
