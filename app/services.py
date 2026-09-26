from dataclasses import dataclass

from app.repositories import (
    CleaningTaskRepository,
    MaintenanceRepository,
    ReservationRepository,
    WebhookRepository,
)

from app.schemas import (
    MaintenanceRequestCreate,
    PaymentWebhookEvent,
    ReservationStatus,
)


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

    def update_status(
        self,
        reservation_id: int,
        status: ReservationStatus,
    ):
        reservation = self.get(reservation_id)
        reservation.status = status.value

        return self.reservations.save(reservation)


@dataclass
class CleaningService:
    reservations: ReservationRepository
    cleaning_tasks: CleaningTaskRepository

    def create_task(self, reservation_id: int):
        reservation = self.reservations.get(reservation_id)

        if reservation is None:
            raise ReservationNotFoundError

        if reservation.status == "cancelled":
            raise InvalidReservationStateError

        return self.cleaning_tasks.create(reservation_id)


@dataclass
class MaintenanceService:
    reservations: ReservationRepository
    maintenance_requests: MaintenanceRepository

    def create_request(
        self,
        reservation_id: int,
        payload: MaintenanceRequestCreate,
    ):
        reservation = self.reservations.get(reservation_id)

        if reservation is None:
            raise ReservationNotFoundError

        if reservation.status == "cancelled":
            raise InvalidReservationStateError

        request = self.maintenance_requests.create(
            reservation_id=reservation.id,
            issue_type=payload.issue_type.value,
            description=payload.description,
            severity=payload.severity.value,
        )

        return {
            "id": request.id,
            "reservation_id": request.reservation_id,
            "property_name": reservation.property_name,
            "issue_type": request.issue_type,
            "description": request.description,
            "severity": request.severity,
            "status": request.status,
        }


@dataclass
class PaymentWebhookService:
    reservations: ReservationRepository
    webhooks: WebhookRepository

    def process(self, event: PaymentWebhookEvent):
        reservation = self.reservations.get(event.reservation_id)

        if reservation is None:
            raise ReservationNotFoundError

        # If the provider retries the exact same event,
        # acknowledge it without repeating the side effect.
        if self.webhooks.has_processed(event.event_id):
            return {
                "event_id": event.event_id,
                "reservation_id": reservation.id,
                "payment_status": reservation.payment_status,
                "payment_notifications_sent": (
                    reservation.payment_notifications_sent
                ),
                "duplicate": True,
            }

        # First delivery: process normally.
        reservation.payment_status = event.status.value

        if event.status.value == "paid":
            reservation.payment_notifications_sent += 1

        self.reservations.save(reservation)

        # Persist the event ID so future retries are recognized.
        self.webhooks.mark_processed(event.event_id)

        return {
            "event_id": event.event_id,
            "reservation_id": reservation.id,
            "payment_status": reservation.payment_status,
            "payment_notifications_sent": (
                reservation.payment_notifications_sent
            ),
            "duplicate": False,
        }