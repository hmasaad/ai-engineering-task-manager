# Data Model: Run One File Read

## Workflow file run

One accepted name for one performed file-read step.

| Field | Rule |
|---|---|
| `id` | Integer. Assigned when the run is stored. |
| `task_id` | The task. Required. |
| `step_id` | The file-read step that was performed. Required. The same step may be named again after a failed read, under a different name. |
| `name` | Trimmed text. Required. Unique on the task. |
| `recorded_at` | The workspace time when the run was stored. Required. |

A second insert for the same task and name does not add a row.

The task detail includes `workflow.runs`, a list of `{name, title}` from oldest run to newest. `title` is the step title. `workflow.can_run_read` is true when the task's next unfinished step is a Pending or Failed file read and no step is Running.

## State

- Before an accepted name, the step stays as it was.
- An accepted read completes the step and stores the file read, the outbox message, and the isolated effect that an advance of that read already stores.
- A file that cannot be read fails the step and stores the run. No file read is stored.
- A rolled-back run leaves the step Pending and leaves no run row.

## Relationships

- A run belongs to one task and one workflow step.
- The stored file read stays the file-read record. The run does not replace it.
- An advance name stays on `workflow_advance`. A run does not write that table.
