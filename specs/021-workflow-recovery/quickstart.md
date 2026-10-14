# Quickstart: Workflow Recovery and Replay

## Checks

```bash
.venv/bin/pytest tests/unit/test_workflow_recovery.py tests/contract/test_workflow_recovery_api.py
.venv/bin/pytest
```

## What the checks cover

- A replay lists the running entry and the result. Opening the same workspace file shows that list and does not read the file again.
- A running step with no effect refuses advance. Recover marks it failed, names the step, and leaves the next step pending.
- A running step whose file read or folder change is already stored is settled from that record, and the action is not repeated.

## Page

On the task, Replay lists each stored entry. While a step is running, the interruption sentence is shown and the button is Recover workflow.
