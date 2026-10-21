# Quickstart: Constrained and Multi-Objective Bayesian Optimization

1. Run `.venv/bin/pytest tests/unit/test_bayesian_optimization.py tests/contract/test_bayesian_optimization_api.py`
2. Run `.venv/bin/pytest`

Expected result: Ada stays at settings 1 and 1. A repeated observation name does not change the constraint. Grace is violated, so the front is ada. Mina and nora both score 2, and the next design is mina. The page shows `Next design: mina`. `GET /api/tasks` stays a list of tasks.
