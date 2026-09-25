# Product Engineer Practice Assessment

**Timebox: 2 hours**

## Scenario

StayOps is a small operations platform for short-term-rental teams.

The system already stores reservations, creates cleaning tasks, and receives payment webhooks. Operations now needs a maintenance workflow, and two existing behaviors have caused problems in production-like testing.

Your goal is to implement the requested behavior without unnecessarily redesigning the application.

---

## Task 1 — Add maintenance requests

Implement:

```http
POST /api/reservations/{reservation_id}/maintenance-requests
```

Request body:

```json
{
  "issue_type": "heating",
  "description": "The bedroom radiator is not warming up.",
  "severity": "medium"
}
```

Supported `issue_type` values:

- `plumbing`
- `access`
- `heating`
- `electrical`
- `other`

Supported `severity` values:

- `low`
- `medium`
- `high`

Expected behavior:

- Return **201** when the request is created.
- Return **404** when the reservation does not exist.
- Return **409** when the reservation is cancelled.
- Invalid enum values should be rejected through normal request validation.
- The created maintenance request starts with status `open`.
- The response should include the property name.
- Keep HTTP concerns in the route and business rules outside the route.

Example response:

```json
{
  "id": 1,
  "reservation_id": 1,
  "property_name": "Marina Loft",
  "issue_type": "heating",
  "description": "The bedroom radiator is not warming up.",
  "severity": "medium",
  "status": "open"
}
```

---

## Task 2 — Fix the cleaning-task bug

Existing endpoint:

```http
POST /api/reservations/{reservation_id}/cleaning-tasks
```

Current bug:

A cleaning task can be created for a reservation whose status is already `cancelled`.

Required behavior:

- Existing reservation + active status → create task as before.
- Missing reservation → **404**.
- Cancelled reservation → **409 Conflict**.
- Keep the business rule in one sensible place rather than duplicating it across routes.

---

## Task 3 — Make payment webhooks idempotent

Existing endpoint:

```http
POST /api/webhooks/payments
```

Payment providers can retry the same webhook. The current implementation processes the same `event_id` more than once.

That means this request sent twice:

```json
{
  "event_id": "evt_1001",
  "reservation_id": 1,
  "status": "paid"
}
```

currently increments the reservation's `payment_notifications_sent` twice.

Required behavior:

- The first delivery should be processed normally.
- A repeated `event_id` must **not** repeat the side effect.
- A duplicate should still receive a successful HTTP response so the provider does not keep retrying.
- The response must make it clear whether the event was a duplicate.
- Missing reservation → **404**.
- Do not solve this with a global Python set; use the persistence layer already present in the project.

---

## Task 4 — Tests

Add focused tests covering at least:

1. successful maintenance request creation;
2. maintenance request for missing reservation;
3. maintenance request for cancelled reservation;
4. cleaning task rejected for cancelled reservation;
5. duplicate payment webhook does not repeat the notification side effect.

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
