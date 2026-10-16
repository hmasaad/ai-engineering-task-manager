# Data Model: Saga Pattern and Compensation

## workflow_compensation

One row withdraws one completed step. A new workspace creates the table. No column is added to an existing table.

| Column | Rule |
|---|---|
| `id` | New row |
| `task_id` | The task |
| `step_id` | The completed step. One compensation for that step. |
| `reason` | Trimmed text, not empty |
| `state` | `Compensated`, `Waiting`, or `Not carried out` |
| `evidence` | Null until a folder compensation is approved. Then the evidence reviewed, not empty |
| `decline_reason` | Null unless the compensation is not carried out. Then trimmed text, not empty |
| `recorded_at` | The time of the compensation |

A file read is stored as `Compensated`. A folder is stored as `Waiting` until it is approved or marked not carried out.

## Saga

Derived from the current version. It is not a stored column.

| Saga | When |
|---|---|
| `Open` | Steps exist and none has failed |
| `Failed` | A step has failed and a completed step is not yet settled |
| `Waiting` | A compensation is waiting |
| `Compensated` | A step has failed and every completed step is compensated or not carried out |

No steps means no saga.

## Task page

`GET /api/tasks` stays the top-level task list. The workflow on the task detail gains `saga` and `compensations`. Each compensation has `id`, `title`, `state`, and `reason`.
