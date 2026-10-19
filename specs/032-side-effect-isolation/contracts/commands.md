# Commands: Deterministic Replay and Side-Effect Isolation

`GET /api/tasks` stays the top-level task list.

The workflow object on a task detail gains `isolated`.

## Replay isolated effects

`POST /api/tasks/{id}/workflow/replay-isolated`

No body. The button is `Replay isolated effects`. The read writes nothing, does not call the clock, and does not open the project.

| Condition | Status | Result |
|---|---|---|
| Steps exist and none is running | 200 | `{matched, stopped}`. Completed steps name their sealed path. |
| No steps | 409 | `There is no isolated effect to replay.` |
| A step is running | 409 | `Recover the interrupted step first.` |
| Unknown task | 404 | `Task not found.` |

`stopped` uses these sentences:

- Pending: `Stopped at {title}: the step has not run.`
- Waiting: `Stopped at {title}: waiting for approval.`
- Failed: `Stopped at {title}: {detail}`
- Completed with no seal: `Stopped at {title}: the isolated effect is missing.`

## Page

When `isolated` is present, the workflow section shows Isolated effects, the matched steps, and the stop sentence. Replay isolated effects is shown when the workflow has steps and is not interrupted.
