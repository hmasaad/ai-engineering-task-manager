# Quickstart: Contextual Bandits and Reinforcement Learning for Workflow Scheduling

## Prerequisites

Python 3.12 and the repository virtual environment. No new package.

## Checks

```bash
.venv/bin/pytest tests/unit/test_contextual_bandits.py tests/contract/test_contextual_bandits_api.py
.venv/bin/pytest
```

The first command covers two actions, four contexts, a reward, a repeated name, the learned total, an untried action, an equal average, a higher average, another context, a rolled-back choice, another task, and the page. The second command confirms the existing suite stays green.

## Expected

- Ada stays one action. A repeated name does not add another.
- One trial of reward 1 stays reward 1 and shows a total of 1 from 1 trial.
- Before any trial, the choice for rush is ada. After ada is tried, the choice is grace. Equal averages choose ada. A higher average for grace chooses grace.
- The page shows `Choice for rush: grace`.
- `GET /api/tasks` stays a list of tasks.
