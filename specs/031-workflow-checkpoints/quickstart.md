# Quickstart: Workflow Snapshots and Checkpointing

## Checks

```bash
.venv/bin/pytest tests/unit/test_workflow_checkpoints.py tests/contract/test_workflow_checkpoints_api.py
.venv/bin/pytest
```

## What the checks cover

- A named checkpoint keeps the original step states when the same name is taken again. A blank name, a task with no steps, a running step, and a rolled-back checkpoint store nothing.
- Restore after a failed read puts that step back to Pending and leaves the completed read in place. A failed step with a stored effect is refused.
- The task page says `No checkpoints yet.` before one is taken, then shows the snapshot. Restore from the page puts the failed step back to Pending.

## Page

Open an In Progress task with two reads. Take `before the read`. Advance until the second step fails. Press Restore checkpoint. The first step stays completed and the second is Pending.
