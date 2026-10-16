# Quickstart: Workflow Replay and Deterministic Execution

## Checks

```bash
.venv/bin/pytest tests/unit/test_deterministic_replay.py tests/contract/test_deterministic_replay_api.py
.venv/bin/pytest
```

## What the checks cover

- A finished workflow reports each completed step and its stored file. A second replay returns the same report and does not read a file again.
- A pending step, a waiting step, and a failed step stop the report without performing the step.
- A missing stored effect stops the report and does not read the file.
- A running step is refused with `Recover the interrupted step first.`
- The task page shows the matched step, the stop sentence, and Replay execution.

## Page

Open an In Progress task whose first workflow step has completed and whose next step is pending. The page shows the matched file and the stop sentence. Press Replay execution. The report stays the same.
