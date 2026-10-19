# Data Model: Replay a Dead Letter

## workflow_dead_letter_replay

One row returns one dead letter to delivery. A new workspace creates the table. No column is added to an existing table. The dead letter is not deleted. `workflow_outbox.state` stays `Pending` or `Delivered`.

| Column | Rule |
|---|---|
| `id` | New row |
| `task_id` | The task |
| `outbox_id` | The dead letter that was returned. One replay for that message |
| `name` | The trimmed replay name. One row for that name on that task |
| `recorded_at` | The workspace time of the replay |

A second insert for the same task and name does not add a row. A second insert for the same message does not add a row. A refused replay and a rolled-back replay have no row.

## Task detail

`GET /api/tasks` stays the top-level task list. The workflow on the task detail gains `dead_letter_replays`.

| Field | Rule |
|---|---|
| `name` | The trimmed replay name |
| `outbox_id` | The message that was returned |
| `title` | The step title |

The list is oldest replay first. It is empty when no replay is stored. A message with a dead letter and a replay is shown as Pending. A message with a dead letter and no replay is shown as Dead. The dead letter list still includes a replayed message.
