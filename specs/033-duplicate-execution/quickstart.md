# Quickstart: Idempotency and Duplicate Execution Control

## Checks

From the repository root:

```bash
.venv/bin/pytest tests/unit/test_duplicate_execution.py tests/contract/test_duplicate_execution_api.py
.venv/bin/pytest
```

## What a passing check shows

- A read named "once" stores one file read. Sending "once" again after the file is removed does not read another file.
- A folder named "notes" stores one folder change. Sending "notes" again after the folder is removed does not create it again.
- A missing file does not save the name. The same name can read the file once it exists.
- A rolled-back read leaves no execution.
- The page shows the named execution, and submitting that name again does not read the file again.
- `GET /api/tasks` stays a list.
