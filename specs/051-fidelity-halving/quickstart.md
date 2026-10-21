# Quickstart: Multi-Fidelity Bayesian Optimization and Successive Halving

1. Run `.venv/bin/pytest tests/unit/test_fidelity_halving.py tests/contract/test_fidelity_halving_api.py`
2. Run `.venv/bin/pytest`

Expected result: Ada stays one candidate after a repeated name. A repeated measurement name does not change the score. Cheap scores ada 1, grace 2, mina 2, and nora 1 keep grace and mina. After grace scores 1 and mina scores 2 at fidelity 2, the winner is mina. The page shows `Winner: mina`. `GET /api/tasks` stays a list of tasks.
