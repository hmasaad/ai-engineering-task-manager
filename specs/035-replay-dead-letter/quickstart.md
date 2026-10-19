# Quickstart: Replay a Dead Letter

## Checks

From the repository root:

```bash
.venv/bin/pytest tests/unit/test_replay_dead_letter.py tests/contract/test_replay_dead_letter_api.py
.venv/bin/pytest
```

## What a passing check shows

- Replaying "once" shows the oldest dead letter as Pending and keeps the dead letter.
- Delivering after that replay marks the message Delivered. The file was read only once.
- A message with three attempts stays at three, and delivery can accept it before the old next time.
- A rolled-back replay leaves the message Dead, and delivery still skips it.
- The page offers Replay dead letter and then shows the replay.
- `GET /api/tasks` stays a list.
