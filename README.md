# StayOps Practice Assessment

A small FastAPI codebase for practicing a Base360-style Product Engineer assessment.

This repository intentionally contains:
- an existing layered backend,
- one missing feature,
- two realistic product bugs,
- a small SQLite database,
- a few baseline tests.

Your job is **not** to redesign the whole application. Read `ASSIGNMENT.md`, understand the current system, make the smallest reliable changes, test them, and be ready to explain every decision.

## Run locally

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open:

- API: http://127.0.0.1:8000
- Swagger: http://127.0.0.1:8000/docs

Run tests:

```bash
pytest -q
```

## Architecture

```text
HTTP request
    ↓
FastAPI route
    ↓
Pydantic schema / validation
    ↓
Service / business logic
    ↓
Repository
    ↓
SQLite database
```

The project uses SQLite so you can focus on the product and engineering decisions rather than local database setup.

## Seed data

On first startup the application creates:

- Reservation 1: confirmed
- Reservation 2: cancelled
- Reservation 3: confirmed

Delete `practice.db` if you want to reset the local database.

## Important

Treat this like a real two-hour assessment:
1. Read the entire assignment before coding.
2. Run the existing tests first.
3. Reproduce the current behavior.
4. Make focused changes.
5. Add tests.
6. Review your diff before finishing.
7. Complete `SUBMISSION.md`.

Do not search for a hidden solution. The point is to practice reasoning through an unfamiliar repository.
