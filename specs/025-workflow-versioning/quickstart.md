# Quickstart: Workflow Versioning and Migration

## Checks

```bash
.venv/bin/pytest tests/unit/test_workflow_versioning.py tests/contract/test_workflow_versioning_api.py
.venv/bin/pytest
```

## What the checks cover

- A new workflow and a workflow that already has steps both show version 1.
- Revise after one completed step creates a draft with that step and without the pending step.
- A new step added during the draft stays off the current version until migration.
- Migration with a reason makes the draft current, keeps the superseded version, and does not perform the completed step again.
- The next advance skips the pending step that was left behind.
- A blank reason, a second draft, a revise before the workflow runs, and an interrupted step are refused.
- The task page shows the version, the draft, and the migration reason.

## Page

Open an In Progress task whose workflow has run. Press Revise workflow. Add the replacement step. Enter the reason and press Migrate workflow. The task shows the new version, and the superseded version stays in the list.
