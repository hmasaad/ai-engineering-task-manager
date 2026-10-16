# Data Model: Workflow Observability and Distributed Tracing

## workflow_trace

One row is the trace for one task. A new workspace creates the table. No column is added to an existing table.

| Column | Rule |
|---|---|
| `id` | New row |
| `task_id` | The task. One trace for that task |
| `recorded_at` | The time the first step started |

## workflow_span

One row is one running of one step.

| Column | Rule |
|---|---|
| `id` | New row |
| `trace_id` | The task's trace |
| `step_id` | The step |
| `parent_id` | Null for the first span. Every later span names the first span |
| `name` | The step title, trimmed, not empty |
| `state` | `Running`, `Completed`, `Failed`, or `Waiting` |
| `detail` | Null, or the step detail, not empty |
| `started_at` | The time the step started |
| `ended_at` | Null while Running. The finish time once the step has completed, failed, or is waiting |

A second running of the same step adds another span. It still follows the first span.

## Task page

`GET /api/tasks` stays the top-level task list. The workflow on the task detail gains `trace`. It is null when the task has no trace. Otherwise it has `id` and `spans`. Each span has `id`, `parent_id`, `name`, `state`, `detail`, `started_at`, and `ended_at`.
