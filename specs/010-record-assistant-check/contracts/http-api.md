# Contract: Assistant check command

A client-supplied assistant name, engineer name, or time is ignored. Extra JSON fields are ignored.

`POST /api/tasks/{id}/implementation-changes/{change_id}/checks` is unchanged. It records the engineer's check and writes no assistant row.

## Record an assistant check

`POST /api/tasks/{id}/assistant-checks`

```json
{
  "change_id": 1,
  "criterion_id": 1,
  "evidence": "The detail page shows the goal in the export",
  "result": "Passed"
}
```

`criterion_id` may be omitted. Omitting it is `Choose an acceptance criterion.` A non-integer `change_id` or `criterion_id` is the wrong-shape message. `evidence` defaults to an empty string. `result` may be omitted.

| Condition | Status | Message |
|---|---|---|
| The body is missing `change_id` or has the wrong shape. | 400 | `The request is missing a required field or has the wrong shape.` |
| The task id does not exist. | 404 | `Task not found.` |
| The task is Draft. | 409 | `The task must be In Progress.` |
| The task is Ready. | 409 | `Start the task first.` |
| The task is Completed. | 409 | `Reopen the task first.` |
| The task is Cancelled. | 409 | `A cancelled task cannot be changed. Continued work is a new task.` |
| `change_id` is unknown. | 404 | `Implementation change not found.` |
| The change is on another task. | 409 | `The check must name a change on that task.` |
| The change is Awaiting approval. | 409 | `The change must be carried out before it can be checked.` |
| The change is Not carried out. | 409 | `A change that was not carried out cannot be checked.` |
| `criterion_id` is omitted. | 400 | `Choose an acceptance criterion.` |
| `criterion_id` is unknown. | 404 | `Acceptance criterion not found.` |
| The criterion is on another task. | 409 | `The check must name a criterion on that task.` |
| `evidence` is blank or only spaces. | 400 | `An account of the evidence is required.` |
| `result` is missing or is neither `Passed` nor `Failed`. | 400 | `Choose Passed or Failed.` |

A success response is 200 and the task detail. The new check is on that change, oldest first, with:

- `criterion_text`, `evidence`, `result` (`Passed` or `Failed`)
- `engineer_name` equal to the workspace engineer
- `assistant_name` equal to the workspace assistant
- `checked_at` equal to the workspace time

The change outcome stays `Carried out`. The task status stays `In Progress`. The criterion state is unchanged.

## Reading checks

`GET /api/tasks/{id}` keeps today's check list. Each check includes `assistant_name`.

- An engineer-recorded check has `assistant_name: null`.
- An assistant-recorded check has the workspace assistant.

A decision's `check` object includes the same `assistant_name` when the decision names a check. It stays null when the decision names no check.

Opening the task does not insert a check. The command does not call a model and does not open a project file.
