# Quickstart: Contextual Bandits with Linear Models and Neural Contextual Bandits

1. Run `.venv/bin/pytest tests/unit/test_linear_bandits.py tests/contract/test_linear_bandits_api.py`
2. Run `.venv/bin/pytest`

Expected result: Rush keeps marks 1 and 1 after a repeated name. Ada's two quiet pulls leave the first weight at 4. Grace's rush pull leaves all three weights at 2. The linear choice in rush is ada. The neural choice in rush is grace. The page shows `Neural choice in rush: grace`. `GET /api/tasks` stays a list of tasks.
