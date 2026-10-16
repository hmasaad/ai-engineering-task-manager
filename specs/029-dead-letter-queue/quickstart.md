# Quickstart: Dead Letter Queues and Poison Messages

## Checks

```bash
.venv/bin/pytest tests/unit/test_dead_letter.py tests/contract/test_dead_letter_api.py
.venv/bin/pytest
```

## What the checks cover

- The third rejection of the oldest message makes it a dead letter. The newer message stays Pending and can be delivered. One earlier rejection still allows that message to be delivered.
- The same rejection name does not count twice. A blank name, a blank reason, and a task with nothing Pending are refused. A rolled-back rejection leaves no poison record and no dead letter.
- The task page shows Reject message, the rejection, and the dead letter. The task list stays a list.

## Page

Open an In Progress task with one Pending outbox message. Enter a rejection name and `The reader stopped.`, then press Reject message. Repeat with two new names. The page shows that message as a dead letter.
