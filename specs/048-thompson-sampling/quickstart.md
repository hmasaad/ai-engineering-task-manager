# Quickstart: Multi-Armed Bandits, Thompson Sampling, and Contextual Exploration

1. Run `.venv/bin/pytest tests/unit/test_thompson_sampling.py tests/contract/test_thompson_sampling_api.py`
2. Run `.venv/bin/pytest`

Expected result: Ada and grace stay as two arms. A repeated pull name does not change the reward. With one win and one loss for ada in rush, and no pull for grace in rush, the middle draw chooses ada and the high draw chooses grace. A win for grace in quiet does not change the rush draw. The page shows `Draw in rush: grace, high sample`. `GET /api/tasks` stays a list of tasks.
