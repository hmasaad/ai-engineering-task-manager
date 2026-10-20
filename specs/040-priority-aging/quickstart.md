# Quickstart: Priority Scheduling, Aging, and Starvation Prevention

## Prerequisites

Python 3.12 and the repository virtual environment. No new package.

## Checks

```bash
.venv/bin/pytest tests/unit/test_priority_aging.py tests/contract/test_priority_aging_api.py
.venv/bin/pytest
```

The first command covers a rank, a highest-score serve, aging, a starvation tie, a rolled-back serve, another task, and the page. The second command confirms the existing suite stays green.

## Expected

- Quiet starts at rank 1, age 0. Rush starts at rank 3, age 0.
- Serve "one" serves rush and leaves quiet at age 1.
- After quiet has aged by 2, serve "three" serves quiet ahead of a new rank of 3.
- A serve with no waiting work is refused with `Rank work before serving.`
- The page shows `quiet: rank 1, age 2` and `one served rush`.
- `GET /api/tasks` stays a list of tasks.
