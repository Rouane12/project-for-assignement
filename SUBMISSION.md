# Submission

## What I changed

- Added `POST /api/reservations/{reservation_id}/guest-issues`.
- Added guest-issue validation and business rules for missing and terminal reservations.
- Included `property_name` and `guest_name` in guest-issue responses.
- Added reservation status-transition rules so only valid state changes are allowed.
- Allowed repeating the current reservation status as a harmless operation.
- Prevented duplicate scheduled cleaning tasks using persisted database state.
- Added focused automated tests covering all required behaviors.

## Assumptions

- `cancelled` and `checked_out` are terminal reservation states.
- Guest issues should only be created for active reservations.
- A reservation should have at most one cleaning task with status `scheduled` at a time.
- Repeating the current reservation status should not perform an unnecessary database update.

## Trade-off made because of the timebox

I kept the existing repository and service structure instead of redesigning the persistence layer or introducing additional abstractions.

The duplicate cleaning-task protection performs a read before create. This is simple and consistent with the existing codebase, but concurrent requests could still both pass the check before either creates the task.

## What I would improve with more time

I would enforce the “one scheduled cleaning task per reservation” rule at the database level as well as in the service layer.

For production, I would use a database constraint or transactional locking strategy so concurrent requests cannot create duplicate scheduled tasks even when they arrive at nearly the same time.