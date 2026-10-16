# Quickstart: Transactional Outbox and Inbox

## Checks

```bash
.venv/bin/pytest tests/unit/test_transactional_outbox.py tests/contract/test_transactional_outbox_api.py
.venv/bin/pytest
```

## What the checks cover

- A completed read stores one Pending outbox message. A failed read stores none. A rolled-back completion stores none.
- Delivering `once` marks the oldest message Delivered. Delivering `once` again does not deliver the next message.
- A blank name and a new name with nothing Pending are refused.
- The same name on another task delivers that task's own message.
- The task page shows the message, Deliver outbox, and the inbox name.

## Page

Open an In Progress task whose workflow step has completed. The outbox shows that step as Pending. Enter `once` and press Deliver outbox. The message is Delivered and the inbox shows `once`.
