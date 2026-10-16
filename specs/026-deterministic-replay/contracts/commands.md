# Commands: Workflow Replay and Deterministic Execution

`GET /api/tasks` stays the top-level task list.

`GET /api/tasks/{id}/workflow-replay` stays the list of step events.

## Replay execution

`POST /api/tasks/{id}/workflow/replay-execution`

No body.

| Condition | Status | Result |
|---|---|---|
| The current version has completed steps with stored effects | 200 | `{"version": 1, "matched": [{"title": "Read the note", "action": "read", "state": "Completed", "effect": "note.txt"}], "stopped": null}` |
| A later step is Pending | 200 | The completed prefix, and `stopped` is `Stopped at {title}: the step has not run.` |
| A step is Waiting | 200 | `stopped` is `Stopped at {title}: waiting for approval.` |
| A step is Failed | 200 | `stopped` is `Stopped at {title}: {detail}` |
| A completed step has no stored effect | 200 | `stopped` is `Stopped at {title}: the stored effect is missing.` |
| No steps | 409 | `There is no step to replay.` |
| A step is Running | 409 | `Recover the interrupted step first.` |
| Unknown task | 404 | `Task not found.` |

A repeated request returns the same report. The task status, step states, file reads, folder changes, and event replay are unchanged.

The workflow object on the task detail includes `execution` with the same report when it can be derived. It is `null` when there are no steps or a step is running.

## Page

The workflow section shows the matched steps in `#workflow-execution` and the stop sentence in `#workflow-execution-stopped` when the report stops. The button is `Replay execution`. It is shown when the workflow has steps and no step is interrupted. Using it shows the same report.
