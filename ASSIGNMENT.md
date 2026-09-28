# Product Engineer Practice Assessment 2

**Timebox: 2 hours**

## Scenario

StayOps is a small operations platform for short-term-rental teams.

The product already stores reservations, creates cleaning tasks, and receives payment webhooks. Operations has reported three problems:

1. guest issues are still being handled manually outside the platform;
2. reservation status updates can move into impossible states;
3. repeated clicks can create duplicate scheduled cleaning tasks for the same stay.

Your goal is to implement the requested behavior without unnecessarily redesigning the application.

---

## Task 1 — Add guest issues

Implement:

```http
POST /api/reservations/{reservation_id}/guest-issues
```

Request body:

```json
{
  "category": "access",
  "description": "The keypad code is being rejected.",
  "urgency": "high"
}
```

Supported `category` values:

- `access`
- `noise`
- `cleanliness`
- `appliance`
- `other`

Supported `urgency` values:

- `low`
- `normal`
- `high`

Expected behavior:

- Return **201** when the guest issue is created.
- Return **404** when the reservation does not exist.
- Return **409** when the reservation is already `cancelled` or `checked_out`.
- Invalid enum values should be rejected through normal request validation.
- New guest issues start with status `open`.
- The response must include both `property_name` and `guest_name` from the reservation.
- Keep HTTP concerns in the route and business rules outside the route.

Example response:

```json
{
  "id": 1,
  "reservation_id": 1,
  "property_name": "Marina Loft",
  "guest_name": "Maya Chen",
  "category": "access",
  "description": "The keypad code is being rejected.",
  "urgency": "high",
  "status": "open"
}
```

Some supporting persistence/schema pieces are already present in the codebase. Inspect before adding new abstractions.

---

## Task 2 — Protect reservation status transitions

Existing endpoint:

```http
PATCH /api/reservations/{reservation_id}/status
```

Current bug:

The endpoint currently allows any valid status to replace any other valid status. That means impossible transitions such as `cancelled -> checked_in` can happen.

Required transition rules:

- `confirmed -> checked_in`
- `confirmed -> cancelled`
- `checked_in -> checked_out`
- repeating the current status is harmless and should return the reservation successfully
- `checked_out` is terminal
- `cancelled` is terminal
- all other transitions → **409 Conflict**
- missing reservation → **404**

Keep the transition rule in one sensible business-logic location.

---

## Task 3 — Prevent duplicate scheduled cleaning tasks

Existing endpoint:

```http
POST /api/reservations/{reservation_id}/cleaning-tasks
```

Current bug:

Calling the endpoint twice for the same active reservation creates two `scheduled` cleaning tasks.

Required behavior:

- Active reservation with no scheduled cleaning task → **201**
- Missing reservation → **404**
- Cancelled reservation → **409**
- If a `scheduled` cleaning task already exists for that reservation → **409**
- Do not solve this with a global Python set or request-local state; determine the answer from persisted data.
- Keep the duplicate rule in the business/service layer, with persistence concerns in the repository.

---

## Task 4 — Tests

Add focused tests covering at least:

1. successful guest-issue creation;
2. guest issue for a missing reservation;
3. guest issue rejected for a terminal reservation;
4. legal reservation status transition succeeds;
5. illegal reservation status transition returns 409;
6. repeating the current reservation status succeeds;
7. duplicate scheduled cleaning task returns 409.

You may add additional tests if useful, but prioritize the required behavior over test volume.

---

## Task 5 — Submission note

Complete `SUBMISSION.md` with:

- what you changed;
- important assumptions;
- one trade-off you made because of the timebox;
- one improvement you would make with more time.

---

## Evaluation

We care about:

- correctness;
- understanding an unfamiliar codebase;
- sensible separation of responsibilities;
- API and status-code judgment;
- data consistency;
- testing;
- pragmatic product thinking;
- ability to explain your decisions.

A small, understandable solution is better than a large redesign.

## Before you start

Run:

```bash
pytest -q
```

Then launch the API and inspect the current behavior through Swagger before changing code.
