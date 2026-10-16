# Quickstart: Saga Pattern and Compensation

## Checks

```bash
.venv/bin/pytest tests/unit/test_saga_compensation.py tests/contract/test_saga_compensation_api.py
.venv/bin/pytest
```

## What the checks cover

- A failed workflow compensates the latest completed read first. The stored file read remains. A blank reason and a workflow that has not failed are refused.
- A completed folder waits. Approval removes an empty folder and keeps the original change. A folder that contains a file stays. Declining leaves the folder.
- A waiting compensation blocks the next one.
- The task page shows Saga Failed, Compensate, and Saga Compensated after the step is withdrawn.

## Page

Open an In Progress task whose workflow has a completed read and a failed step. The page shows Saga Failed. Enter the reason and press Compensate. The page shows that step and Saga Compensated.
