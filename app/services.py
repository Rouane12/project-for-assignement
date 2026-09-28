from dataclasses import dataclass

from app.repositories import (
    CleaningTaskRepository,
    GuestIssueRepository,
    ReservationRepository,
    WebhookRepository,
)

from app.schemas import (
    GuestIssueCreate,
    PaymentWebhookEvent,
    ReservationStatus,
)


class ReservationNotFoundError(Exception):
    pass


class InvalidReservationStateError(Exception):
    pass


class DuplicateCleaningTaskError(Exception):
    pass


@dataclass
class ReservationService:
    reservations: ReservationRepository

    def get(
        self,
        reservation_id: int,
    ):
        reservation = self.reservations.get(
            reservation_id
        )

        if reservation is None:
            raise ReservationNotFoundError

        return reservation

    def update_status(
        self,
        reservation_id: int,
        status: ReservationStatus,
    ):
        reservation = self.get(
            reservation_id
        )

        current_status = reservation.status
        new_status = status.value

        # Repeating the same status is harmless.
        if current_status == new_status:
            return reservation

        allowed_transitions = {
            "confirmed": {
                "checked_in",
                "cancelled",
            },
            "checked_in": {
                "checked_out",
            },
            "checked_out": set(),
            "cancelled": set(),
        }

        if new_status not in allowed_transitions.get(
            current_status,
            set(),
        ):
            raise InvalidReservationStateError

        reservation.status = new_status

        return self.reservations.save(
            reservation
        )


@dataclass
class CleaningService:
    reservations: ReservationRepository
    cleaning_tasks: CleaningTaskRepository

    def create_task(
        self,
        reservation_id: int,
    ):
        reservation = self.reservations.get(
            reservation_id
        )

        if reservation is None:
            raise ReservationNotFoundError

        if reservation.status == "cancelled":
            raise InvalidReservationStateError

        if self.cleaning_tasks.has_scheduled_for_reservation(
            reservation_id
        ):
            raise DuplicateCleaningTaskError

        return self.cleaning_tasks.create(
            reservation_id
        )


@dataclass
class GuestIssueService:
    reservations: ReservationRepository
    guest_issues: GuestIssueRepository

    def create_issue(
        self,
        reservation_id: int,
        payload: GuestIssueCreate,
    ):
        reservation = self.reservations.get(
            reservation_id
        )

        if reservation is None:
            raise ReservationNotFoundError

        if reservation.status in {
            "cancelled",
            "checked_out",
        }:
            raise InvalidReservationStateError

        issue = self.guest_issues.create(
            reservation_id=reservation.id,
            category=payload.category.value,
            description=payload.description,
            urgency=payload.urgency.value,
        )

        return {
            "id": issue.id,
            "reservation_id": issue.reservation_id,
            "property_name": reservation.property_name,
            "guest_name": reservation.guest_name,
            "category": issue.category,
            "description": issue.description,
            "urgency": issue.urgency,
            "status": issue.status,
        }


@dataclass
class PaymentWebhookService:
    reservations: ReservationRepository
    webhooks: WebhookRepository

    def process(
        self,
        event: PaymentWebhookEvent,
    ):
        reservation = self.reservations.get(
            event.reservation_id
        )

        if reservation is None:
            raise ReservationNotFoundError

        reservation.payment_status = (
            event.status.value
        )

        if event.status.value == "paid":
            reservation.payment_notifications_sent += 1

        self.reservations.save(
            reservation
        )

        return {
            "event_id": event.event_id,
            "reservation_id": reservation.id,
            "payment_status": (
                reservation.payment_status
            ),
            "payment_notifications_sent": (
                reservation.payment_notifications_sent
            ),
            "duplicate": False,
        }