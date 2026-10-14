# Data Model: Idempotency and Exactly-Once Effects

## Step effect

No new column. A running attempt still stores `workflow_attempt.effect_before`.

- A read effect is a file read on the task past that baseline. The step becomes Completed. The file is not read again.
- A folder effect is a change id above that baseline, or `workflow_step.change_id` when the step is already Failed. The step becomes Completed, Waiting, or stays Failed from that change. The action is not called.

A Failed step whose `change_id` is null has no stored effect and may be retried.

## workflow_advance

One row is one saved advance name for one task. A new workspace creates the table. No column is added to an existing table.

| Column | Rule |
|---|---|
| `task_id` | References `task(id)`. Part of the primary key |
| `name` | Trimmed text, not empty. Part of the primary key |
| `step_id` | References `workflow_step(id)`. The step that name was for |

Primary key: `(task_id, name)`.

The row is inserted when that name is accepted for that step. A blank name inserts nothing. The same trimmed name on another task is a different row.

A later request with that name:

- Running: no write, `Recover the interrupted step first.`
- Waiting: settle that step only
- Completed or Failed: no write and no replay entry

## Task page

The advance form includes the field `name`, label `Advance name`, id `advance-name`. The page fills a new non-empty value each time the task is shown.

`GET /api/tasks` stays the top-level task list. Task detail gains no new workflow field.
