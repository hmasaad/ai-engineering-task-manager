# Quickstart: Bounded Delivery Retries

## Checks

From the repository root:

```bash
.venv/bin/pytest tests/unit/test_bounded_retries.py tests/contract/test_bounded_retries_api.py
.venv/bin/pytest
```

## What a passing check shows

- An unsuccessful delivery named "once" stores one attempt and a next time one minute later. The message stays Pending.
- A delivery before that time is refused with `This delivery is not due yet.` and does not add an attempt.
- After that time, a delivery marks the message Delivered and leaves the count at 1.
- The third unsuccessful delivery writes one dead letter, `The delivery was attempted too many times.`, and the count stays 3.
- A rolled-back third attempt leaves the count at 2 and leaves no dead letter.
- The page shows the attempt count and Delivery did not succeed.
- `GET /api/tasks` stays a list.
