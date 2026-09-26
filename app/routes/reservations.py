from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db

from app.repositories import (
    CleaningTaskRepository,
    MaintenanceRepository,
    ReservationRepository,
)

from app.schemas import (
    CleaningTaskOut,
    MaintenanceRequestCreate,
    MaintenanceRequestOut,
    ReservationOut,
    ReservationStatusUpdate,
)

from app.services import (
    CleaningService,
    InvalidReservationStateError,
    MaintenanceService,
    ReservationNotFoundError,
    ReservationService,
)


router = APIRouter(
    prefix="/api/reservations",
    tags=["reservations"],
)


@router.get(
    "/{reservation_id}",
    response_model=ReservationOut,
)
def get_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
):
    service = ReservationService(
        ReservationRepository(db)
    )

    try:
        return service.get(reservation_id)

    except ReservationNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Reservation not found",
        )


@router.patch(
    "/{reservation_id}/status",
    response_model=ReservationOut,
)
def update_reservation_status(
    reservation_id: int,
    payload: ReservationStatusUpdate,
    db: Session = Depends(get_db),
):
    service = ReservationService(
        ReservationRepository(db)
    )

    try:
        return service.update_status(
            reservation_id,
            payload.status,
        )

    except ReservationNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Reservation not found",
        )


@router.post(
    "/{reservation_id}/cleaning-tasks",
    response_model=CleaningTaskOut,
    status_code=201,
)
def create_cleaning_task(
    reservation_id: int,
    db: Session = Depends(get_db),
):
    service = CleaningService(
        reservations=ReservationRepository(db),
        cleaning_tasks=CleaningTaskRepository(db),
    )

    try:
        return service.create_task(reservation_id)

    except ReservationNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Reservation not found",
        )

    except InvalidReservationStateError:
        raise HTTPException(
            status_code=409,
            detail="Cannot create cleaning task for cancelled reservation",
        )


@router.post(
    "/{reservation_id}/maintenance-requests",
    response_model=MaintenanceRequestOut,
    status_code=201,
)
def create_maintenance_request(
    reservation_id: int,
    payload: MaintenanceRequestCreate,
    db: Session = Depends(get_db),
):
    service = MaintenanceService(
        reservations=ReservationRepository(db),
        maintenance_requests=MaintenanceRepository(db),
    )

    try:
        return service.create_request(
            reservation_id,
            payload,
        )

    except ReservationNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Reservation not found",
        )

    except InvalidReservationStateError:
        raise HTTPException(
            status_code=409,
            detail=(
                "Cannot create maintenance request "
                "for cancelled reservation"
            ),
        )