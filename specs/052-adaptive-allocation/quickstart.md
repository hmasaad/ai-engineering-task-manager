# Quickstart: Adaptive Resource Allocation for Workflow and Agent Optimization

1. Run `.venv/bin/pytest tests/unit/test_adaptive_allocation.py tests/contract/test_adaptive_allocation_api.py`
2. Run `.venv/bin/pytest`

Expected result: Ada stays one agent after a repeated name. A repeated yield name does not change the value. Ada's yield of 2 and grace's yield of 1 store shares of 3 and 1. The page shows `ada: 3`. `GET /api/tasks` stays a list of tasks.
