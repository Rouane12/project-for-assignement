from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from app.database import get_db

from app.repositories import (
    CleaningTaskRepository,
    GuestIssueRepository,
    ReservationRepository,
)

from app.schemas import (
    CleaningTaskOut,
    GuestIssueCreate,
    GuestIssueOut,
    ReservationOut,
    ReservationStatusUpdate,
)

from app.services import (
    CleaningService,
    DuplicateCleaningTaskError,
    GuestIssueService,
    InvalidReservationStateError,
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
        return service.get(
            reservation_id
        )

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

    except InvalidReservationStateError:
        raise HTTPException(
            status_code=409,
            detail=(
                "Invalid reservation "
                "status transition"
            ),
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
        return service.create_task(
            reservation_id
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
                "Cannot create cleaning task "
                "for cancelled reservation"
            ),
        )

    except DuplicateCleaningTaskError:
        raise HTTPException(
            status_code=409,
            detail=(
                "Scheduled cleaning task "
                "already exists"
            ),
        )


@router.post(
    "/{reservation_id}/guest-issues",
    response_model=GuestIssueOut,
    status_code=201,
)
def create_guest_issue(
    reservation_id: int,
    payload: GuestIssueCreate,
    db: Session = Depends(get_db),
):
    service = GuestIssueService(
        reservations=ReservationRepository(db),
        guest_issues=GuestIssueRepository(db),
    )

    try:
        return service.create_issue(
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
                "Cannot create guest issue "
                "for terminal reservation"
            ),
        )