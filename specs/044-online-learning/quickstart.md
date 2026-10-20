# Quickstart: Online Learning and Predictive Workflow Scheduling

## Prerequisites

Python 3.12 and the repository virtual environment. No new package.

## Checks

```bash
.venv/bin/pytest tests/unit/test_online_learning.py tests/contract/test_online_learning_api.py
.venv/bin/pytest
```

The first command covers a length, a limit of 4 outcomes, a repeated name, the learned prediction, a tie, a forecast, the stored schedule, a rolled-back prediction, another task, and the page. The second command confirms the existing suite stays green.

## Expected

- Past stays review took 2. A repeated name does not change it.
- One 1-day review and one 2-day review still predict 1 day. A second 2-day review predicts 2 days.
- Draft starts on day 0 for 2 days, ship starts on day 2 for 1 day, and the finish day is 3.
- The page shows `Finish day: 3`.
- `GET /api/tasks` stays a list of tasks.
