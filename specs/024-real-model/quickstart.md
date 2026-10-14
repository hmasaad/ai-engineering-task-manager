# Quickstart: Real Model

## Checks

```bash
.venv/bin/pytest tests/unit/test_instruction_page.py tests/contract/test_instruction_page_api.py
.venv/bin/pytest
```

## What the checks cover

- A saved service is shown again after the same workspace file is opened. A blank name or address keeps the saved service.
- Starting work on an existing file asks the service once with the file text and what changed, leaves the file unchanged, and shows the reply as waiting for approval.
- A new ordinary file contains the reply.
- An unreachable service and an empty reply store no task and write no file.
- Instructions shows Model address and API key, and does not show Model text.

## Page

Open Instructions. Save the model name and service address. Start work on an existing file. The task shows the reply and the file on disk is unchanged until approval.
