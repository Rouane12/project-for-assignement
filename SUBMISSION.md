# Submission

## What I changed

- Added `POST /api/reservations/{reservation_id}/maintenance-requests`.
- Added maintenance-request validation and business rules for missing and cancelled reservations.
- Included the reservation's `property_name` in the maintenance response.
- Fixed cleaning-task creation so cancelled reservations return `409 Conflict`.
- Made payment webhook processing idempotent using the existing persistent webhook repository.
- Duplicate payment events now return a successful response with `duplicate: true` without repeating the notification side effect.
- Added focused automated tests for the required behaviors.

## Assumptions

- Only reservations with status `cancelled` should be blocked from creating maintenance requests or cleaning tasks, since no other restricted states were specified.
- A repeated payment webhook uses the same `event_id`.
- `event_id` is the identifier used to determine whether a webhook has already been processed.
- `property_name` should be retrieved from the reservation rather than supplied by the client.

## Trade-off made because of the timebox

I kept the existing repository and transaction structure rather than redesigning the persistence layer.

The reservation update and the processed-webhook record are currently saved separately. This keeps the solution small and consistent with the existing codebase, but leaves a small failure window between processing the payment and recording the event as processed.

## What I would improve with more time

I would make payment processing and webhook-event persistence atomic within a single database transaction.

I would also handle concurrent duplicate deliveries using the unique `event_id` constraint so that two workers receiving the same webhook at nearly the same time cannot both perform the side effect.