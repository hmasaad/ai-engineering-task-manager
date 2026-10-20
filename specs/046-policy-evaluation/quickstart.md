# Quickstart: Offline Reinforcement Learning and Policy Evaluation

## Prerequisites

Python 3.12 and the repository virtual environment. No new package.

## Checks

```bash
.venv/bin/pytest tests/unit/test_policy_evaluation.py tests/contract/test_policy_evaluation_api.py
.venv/bin/pytest
```

The first command covers a reward, a limit of 4 logged steps, a repeated name, one rule for one state, a replaced action, a matching score, a policy that matches nothing, a rolled-back score, another task, and the page. The second command confirms the existing suite stays green.

## Expected

- One stays rush, ada, reward 1. A repeated name does not change it.
- Rush takes grace, and quiet takes ada. The score is a total of 4 from 2 steps.
- A rule whose action matches no logged step is refused with `No logged step matches this policy.`
- The page shows `Score: 4 from 2`.
- `GET /api/tasks` stays a list of tasks.
