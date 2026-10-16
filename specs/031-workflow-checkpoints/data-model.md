# Data Model: Workflow Snapshots and Checkpointing

## workflow_checkpoint

One row is one named snapshot for one task. A new workspace creates the table. No column is added to an existing table.

| Column | Rule |
|---|---|
| `id` | New row |
| `task_id` | The task. Together with `name`, one checkpoint |
| `name` | Trimmed text, not empty |
| `recorded_at` | The time the checkpoint was taken |

The same name on the same task does not add a second row. The same name on another task can.

## workflow_checkpoint_step

One row is one step as it stood when the checkpoint was taken.

| Column | Rule |
|---|---|
| `checkpoint_id` | The checkpoint. Together with `step_id`, one stored step |
| `step_id` | The step |
| `position` | The step's place, starting at 1 |
| `state` | `Pending`, `Completed`, `Failed`, or `Waiting` |
| `detail` | Null, or the step detail, not empty |

The steps are stored in workflow order. A later read joins the step title.

## Task page

`GET /api/tasks` stays the top-level task list. The workflow on the task detail gains `checkpoints`. Each one has `id`, `name`, and `steps`. Each step has `title` and `state`.
