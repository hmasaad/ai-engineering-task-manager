# Commands: Workflow Observability and Distributed Tracing

`GET /api/tasks` stays the top-level task list.

The workflow object on a task detail gains `trace`. It is null, or `{id, spans}`.

## Read the trace

`GET /api/tasks/{id}/workflow/trace`

The read writes nothing and does not call the clock.

| Condition | Status | Result |
|---|---|---|
| The task has a trace | 200 | `{"id": 1, "spans": [...]}` |
| The task has no trace | 200 | `{"id": null, "spans": []}` |
| Unknown task | 404 | `Task not found.` |

Each span has `id`, `parent_id`, `name`, `state`, `detail`, `started_at`, and `ended_at`. `parent_id` is null on the first span. A running span has `ended_at` null.

## Page

The workflow section shows `No trace yet.` when `trace` is null. Otherwise it shows `Trace {id}` and each span in order: the name, the state, `follows {parent_id}` when it has a parent, the start, and the end.
