# Quickstart: Safe Exploration, Causal Inference, and Counterfactual Evaluation

## Prerequisites

Python 3.12 and the repository virtual environment. No new package.

## Checks

```bash
.venv/bin/pytest tests/unit/test_safe_exploration.py tests/contract/test_safe_exploration_api.py
.venv/bin/pytest
```

The first command covers a risk, a limit of 2 actions, a safe probe, a risk-2 refusal, a limit of 4 probes, an effect of 1, an effect of -1, an effect of 0, a self comparison, a rolled-back effect, another task, and the page. The second command confirms the existing suite stays green.

## Expected

- Ada stays at risk 1. A repeated name does not change it.
- A probe of a risk-2 action is refused with `That action is not safe to explore.`
- Grace instead of ada in rush has effect 1 when grace's reward is 2 and ada's reward is 1.
- The page shows `Effect of grace instead of ada in rush: 1`.
- `GET /api/tasks` stays a list of tasks.
