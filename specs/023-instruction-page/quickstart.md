# Quickstart: Instruction Page

## Checks

```bash
.venv/bin/pytest tests/unit/test_instruction_page.py tests/contract/test_instruction_page_api.py
.venv/bin/pytest
```

## What the checks cover

- A saved model is shown again after the same workspace file is opened.
- A blank model name or text keeps the saved model.
- Starting work writes a new ordinary file with the model text, stores one file read, and leaves the task In Progress.
- Starting work on an existing file waits and leaves the file unchanged.
- A missing model or a missing file stores no task.
- The task list links to Instructions, and the page shows the model and task fields.

## Page

Open Instructions from the task list. Save the model, then start work. The task page shows the file read and the model text.
