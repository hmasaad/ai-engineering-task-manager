# Quickstart: Multi-Tenant Workflow Scheduling, Fairness, and Resource Quotas

## Prerequisites

Python 3.12 and the repository virtual environment. No new package.

## Checks

```bash
.venv/bin/pytest tests/unit/test_schedule_tenants.py tests/contract/test_schedule_tenants_api.py
.venv/bin/pytest
```

The first command covers an admission, a fair grant, a full quota, a rolled-back turn, another task, and the page. The second command confirms the existing suite stays green.

## Expected

- Ada and grace each start at 0 of 2.
- Turns "one" and "three" go to ada. Turns "two" and "four" go to grace.
- Turn "five" is refused with `Every tenant is at its quota.`
- The page shows `ada: 2 of 2` and `one granted to ada`.
- `GET /api/tasks` stays a list of tasks.
