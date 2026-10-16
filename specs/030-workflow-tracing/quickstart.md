# Quickstart: Workflow Observability and Distributed Tracing

## Checks

```bash
.venv/bin/pytest tests/unit/test_workflow_tracing.py tests/contract/test_workflow_tracing_api.py
.venv/bin/pytest
```

## What the checks cover

- Two completed reads share one trace. The later span follows the first. A missing file closes a failed span. A running step has no end. A rolled-back start leaves no trace.
- Reading the trace twice returns the same spans and does not move the clock. An unknown task is refused with `Task not found.`
- The task page says `No trace yet.` before the workflow runs, then shows the trace and the completed span.

## Page

Open an In Progress task and add a read step. The page says `No trace yet.` Advance the workflow. The page shows the trace and that step as completed.
