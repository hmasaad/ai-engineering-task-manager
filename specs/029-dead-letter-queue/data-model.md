# Data Model: Dead Letter Queues and Poison Messages

## workflow_poison

One row is one named rejection of one outbox message. A new workspace creates the table. No column is added to an existing table.

| Column | Rule |
|---|---|
| `task_id` | The task. Together with `name`, one rejection |
| `name` | Trimmed text, not empty |
| `outbox_id` | The Pending message that was rejected |
| `reason` | Trimmed text, not empty |
| `recorded_at` | The time of the rejection |

The same name on the same task does not add a second row. The same name on another task can.

## workflow_dead_letter

One row sets one outbox message aside. It is stored on the third rejection of that message.

| Column | Rule |
|---|---|
| `id` | New row |
| `task_id` | The task |
| `outbox_id` | The message. One dead letter for that message |
| `reason` | The reason from the third rejection, trimmed, not empty |
| `recorded_at` | The time of that third rejection |

The outbox row stays. Its stored state stays Pending. A reader treats a message with a dead letter as Dead.

## Task page

`GET /api/tasks` stays the top-level task list. The workflow on the task detail gains `poison` and `dead_letters`. An outbox message that has a dead letter is shown as Dead. Each poison entry has `name`, `outbox_id`, and `reason`. Each dead letter has `outbox_id`, `title`, `effect`, and `reason`.
