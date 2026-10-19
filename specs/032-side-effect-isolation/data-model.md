# Data Model: Deterministic Replay and Side-Effect Isolation

## workflow_isolated_effect

One row seals the effect of one completed step. A new workspace creates the table. No column is added to an existing table.

| Column | Rule |
|---|---|
| `id` | New row |
| `task_id` | The task |
| `step_id` | The completed step. One seal for that step |
| `effect` | The file or folder path, trimmed, not empty |
| `recorded_at` | The time the step completed |

A second completion of that step does not add a row. A failed step and a waiting step have no row.

## Isolated replay

Derived from the current steps and these seals. It is not a stored report.

| Field | Rule |
|---|---|
| `matched` | Completed steps that have a seal, in workflow order. Each has `title` and `effect` |
| `stopped` | Null when every step is completed and sealed. Otherwise the sentence for the first step that stops the walk |

No steps, or a running step, means the task detail has no isolated report.

## Task page

`GET /api/tasks` stays the top-level task list. The workflow on the task detail gains `isolated`. It is null when there are no steps or a step is running. Otherwise it is the report above.
