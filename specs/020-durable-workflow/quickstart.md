# Quickstart: Durable Workflow Orchestration

## Checks

```bash
.venv/bin/pytest tests/unit/test_workflow.py tests/contract/test_workflow_api.py
.venv/bin/pytest
```

## What the checks cover

- A step is stored in order, a blank title stores nothing, and a step can be removed only while every step is Pending.
- One advance completes the first step. Opening the same workspace file shows that state, and the next advance performs the following step without repeating the first.
- A missing file stores Failed, names the step, and leaves the next step Pending. The following advance retries only that step.
- A consequential folder waits, a second advance does not record another change, and the advance after approval completes that step without performing it again.

## Page

On an In Progress task, the Workflow section lists each step. Advance workflow runs one step. A stop sentence appears under the Workflow heading while a step is Failed or Waiting.
