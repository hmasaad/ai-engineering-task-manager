# Quickstart: Deterministic Replay and Side-Effect Isolation

## Checks

```bash
.venv/bin/pytest tests/unit/test_side_effect_isolation.py tests/contract/test_side_effect_isolation_api.py
.venv/bin/pytest
```

## What the checks cover

- A completed read seals one effect. A missing file seals nothing. A rolled-back completion seals nothing. A second completion does not add a seal.
- After the file or the folder is removed, replay still names the seal and leaves the project as it was. A second replay matches and does not move the clock.
- The task page shows the sealed effect and Replay isolated effects. The task list stays a list.

## Page

Open an In Progress task whose read has completed. The page shows the sealed file. Press Replay isolated effects. The file was read only once.
