# Data Model: Bounded Delivery Retries

## workflow_delivery_retry

One row records one accepted unsuccessful delivery. A new workspace creates the table. No column is added to an existing table. `workflow_outbox.state` stays `Pending` or `Delivered`.

| Column | Rule |
|---|---|
| `id` | New row |
| `task_id` | The task |
| `outbox_id` | The Pending message this attempt counted |
| `name` | The trimmed attempt name. One row for that name on that task |
| `next_eligible_at` | One minute after the workspace time of this attempt |
| `recorded_at` | The workspace time of this attempt |

A second insert for the same task and name does not add a row. A refused attempt and a rolled-back attempt have no row. At most three rows belong to one message. The third row is stored in the same result as one `workflow_dead_letter` row whose reason is `The delivery was attempted too many times.`

## Task detail

`GET /api/tasks` stays the top-level task list. The workflow on the task detail gains `retries`.

| Field | Rule |
|---|---|
| `outbox_id` | The message |
| `attempt_count` | How many attempts are stored for that message. It stops at 3 |
| `next_eligible_at` | The next time from the latest attempt |

The list is oldest message first. It is empty when no attempt is stored.
