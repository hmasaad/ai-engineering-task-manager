# Data Model: Transactional Outbox and Inbox

## workflow_outbox

One row is one message for one completed step. A new workspace creates the table. No column is added to an existing table.

| Column | Rule |
|---|---|
| `id` | New row |
| `task_id` | The task |
| `step_id` | The completed step. One message for that step. |
| `effect` | The file or folder path stored by the step, not empty |
| `state` | `Pending` or `Delivered` |
| `recorded_at` | The time of the completion |

A second insert for the same step does not add a row.

## workflow_inbox

One row is one accepted delivery name for one task.

| Column | Rule |
|---|---|
| `task_id` | The task |
| `name` | Trimmed text, not empty. Unique for the task. |
| `outbox_id` | The message that this name delivered |
| `recorded_at` | The time of the delivery |

The same name on another task is another row.

## Task page

`GET /api/tasks` stays the top-level task list. The workflow on the task detail gains `outbox` and `inbox`. An empty outbox is an empty list. The page says `No outbox messages yet.` when that list is empty.
