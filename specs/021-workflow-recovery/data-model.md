# Data Model: Workflow Recovery and Replay

## workflow_step

`state` may be `Pending`, `Running`, `Completed`, `Waiting`, or `Failed`. A new workspace creates the table with that check. No column is added.

`Running` means the start is stored and the result is not.

## workflow_attempt

One row for the running attempt of one step.

| Column | Rule |
|---|---|
| `step_id` | Primary key, references `workflow_step(id)` |
| `effect_before` | Integer, zero or greater. For a read, the number of file reads on the task. For a folder, the highest change id on the task, or 0 |

The row is inserted when the step becomes `Running` and removed when the result is stored.

## workflow_event

One row is one replay entry.

| Column | Rule |
|---|---|
| `id` | Integer primary key |
| `task_id` | References `task(id)` |
| `step_id` | References `workflow_step(id)` |
| `state` | `Running`, `Completed`, `Waiting`, or `Failed` |
| `detail` | Null, the action message, the decline reason, or `the step was interrupted.` |
| `recorded_at` | The workspace time |

Index: `(task_id, id)`.

Entries are read in `id` order. The title comes from the step.

## Task detail

`workflow` gains:

| Field | Rule |
|---|---|
| `replay` | The entries, each as `id`, `step_id`, `title`, `state`, `detail`, and `recorded_at` |
| `interrupted` | True when any step is `Running` |

`stopped` for a running step is `Stopped at {title}: the step was interrupted.`

## State changes

- Prepare commits `Running`, one attempt row, and one replay entry. It does not perform the action.
- Finish performs a `Running` step and commits the result entry, then removes the attempt.
- Advance on a `Running` step is refused and writes nothing.
- Recover on a `Running` step with no newer effect, or with no attempt row, commits `Failed` and `the step was interrupted.`
- Recover on a newer file read commits `Completed` and does not read. Recover on a newer folder change commits that change's outcome and does not record another change.
- Reading the replay writes nothing.
