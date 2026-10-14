# Quickstart: Idempotency and Exactly-Once Effects

## Checks

```bash
.venv/bin/pytest tests/unit/test_exactly_once.py tests/contract/test_exactly_once_api.py
.venv/bin/pytest
```

## What the checks cover

- Finishing a running read whose file read is already stored marks the step completed and does not read the file again.
- Advancing again after a declined folder change leaves that one change, the same failure sentence, and the next step pending.
- The advance name "once" completes a read and does not create the following folder. The same name again adds no replay entry. A different name creates the folder.
- A blank name is not saved, and a second blank advance can perform the next step.
- The same name on another task still performs that task's step.
- A name sent while the task is not In Progress is not saved.
- The task page shows Advance name, and submitting a name that already advanced leaves the next step pending.

## Page

The advance form shows Advance name with a filled-in value. After the task is shown again, the value is different.
