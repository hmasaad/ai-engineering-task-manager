# Quickstart: Constraint Programming and Optimization for Workflow Scheduling

## Prerequisites

Python 3.12 and the repository virtual environment. No new package.

## Checks

```bash
.venv/bin/pytest tests/unit/test_constraint_optimization.py tests/contract/test_constraint_optimization_api.py
.venv/bin/pytest
```

The first command covers a length, a limit of 4 activities, a precedence constraint, a cycle, capacity, the earliest finish day, a tie, a rolled-back plan, another task, and the page. The second command confirms the existing suite stays green.

## Expected

- Design stays at length 1. A repeated name does not change it.
- Test starts after build. A cycle is refused with `Those activities would form a cycle.`
- With capacity 2, design starts on day 0, build starts on day 0, test starts on day 2, and the finish day is 3.
- With capacity 1, design starts on day 0, build starts on day 1, test starts on day 3, and the finish day is 4.
- The page shows `Finish day: 3`.
- `GET /api/tasks` stays a list of tasks.
