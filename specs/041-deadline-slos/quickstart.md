# Quickstart: Deadline-Aware Scheduling and Service-Level Objectives (SLOs)

## Prerequisites

Python 3.12 and the repository virtual environment. No new package.

## Checks

```bash
.venv/bin/pytest tests/unit/test_deadline_slos.py tests/contract/test_deadline_slos_api.py
.venv/bin/pytest
```

The first command covers a deadline, an earliest-deadline service, a met result, a missed result, a rolled-back service, another task, and the page. The second command confirms the existing suite stays green.

## Expected

- Export keeps the deadline `2026-12-01T00:00:00Z`. A repeated name does not change it.
- Serve "one" serves the earlier deadline and records missed when that deadline has passed.
- Serve "two" serves the later deadline and records met.
- A service after every objective has been served is refused with `Every objective has been served.`
- The page shows `export: due 2026-12-01T00:00:00Z` and `one missed rush`.
- `GET /api/tasks` stays a list of tasks.
