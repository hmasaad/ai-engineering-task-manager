# Quickstart: Asynchronous Hyperband, ASHA, and Distributed Agent Scheduling

1. Run `.venv/bin/pytest tests/unit/test_asha_scheduling.py tests/contract/test_asha_scheduling_api.py`
2. Run `.venv/bin/pytest`

Expected result: Red stays one trial after a repeated name. A repeated rung-score name does not change the score. After red scores 1 and blue scores 2 at rung 1, the schedule assigns blue to ada. After four rung 1 scores, the second schedule assigns gold to grace. After blue scores 1 and gold scores 2 at rung 2, the winner is gold. The page shows `blue: ada`. `GET /api/tasks` stays a list of tasks.
