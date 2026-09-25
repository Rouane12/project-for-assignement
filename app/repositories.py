from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models


class ReservationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, reservation_id: int) -> models.Reservation | None:
        return self.db.get(models.Reservation, reservation_id)

    def save(self, reservation: models.Reservation) -> models.Reservation:
        self.db.add(reservation)
        self.db.commit()
        self.db.refresh(reservation)
        return reservation


class CleaningTaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, reservation_id: int) -> models.CleaningTask:
        task = models.CleaningTask(reservation_id=reservation_id, status="scheduled")
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task


class MaintenanceRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        *,
        reservation_id: int,
        issue_type: str,
        description: str,
        severity: str,
    ) -> models.MaintenanceRequest:
        request = models.MaintenanceRequest(
            reservation_id=reservation_id,
            issue_type=issue_type,
            description=description,
            severity=severity,
            status="open",
        )
        self.db.add(request)
        self.db.commit()
        self.db.refresh(request)
        return request


class WebhookRepository:
    def __init__(self, db: Session):
        self.db = db

    def has_processed(self, event_id: str) -> bool:
        statement = select(models.ProcessedWebhook).where(
            models.ProcessedWebhook.event_id == event_id
        )
        return self.db.scalar(statement) is not None

    def mark_processed(self, event_id: str) -> None:
        self.db.add(models.ProcessedWebhook(event_id=event_id))
        self.db.commit()
