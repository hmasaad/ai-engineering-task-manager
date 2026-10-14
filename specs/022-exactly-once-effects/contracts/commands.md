# Commands: Idempotency and Exactly-Once Effects

`GET /api/tasks` stays the top-level task list. Advance keeps its current result when `name` is missing or blank.

## Advance

`POST /api/tasks/{task_id}/workflow/advance`

Optional JSON body: `{"name": "once"}`. Extra fields are ignored. The page posts the same field as `name`.

The name is trimmed. A blank name is not saved.

| Condition | Status | Result |
|---|---|---|
| Unknown task | 404 | `Task not found.` |
| Draft task | 409 | `The task must be In Progress.` The name is not saved. |
| Ready task | 409 | `Start the task first.` The name is not saved. |
| Completed task | 409 | `Reopen the task first.` The name is not saved. |
| Cancelled task | 409 | `A cancelled task cannot be changed. Continued work is a new task.` The name is not saved. |
| Nothing left to run | 409 | `There is no step to run.` The name is not saved. |
| First unfinished step is Running | 409 | `Recover the interrupted step first.` The name is not saved. |
| The saved name belongs to a step that is still Running | 409 | `Recover the interrupted step first.` Nothing is performed. |
| First accepted use of the name | 200 | The task detail. One step is performed, or a waiting step is settled, or a failed step that already has its change stays failed. |
| Same name after that step is no longer Running | 200 | The task detail. No step is performed, no second effect is stored, and the replay does not gain an entry. |

A Failed step with a stored folder change stays Failed on a later advance, named or not. No second change is recorded. A Failed step with no stored effect still retries when the advance is allowed to run that step.

The task page field is `advance-name`, label `Advance name`. Each time the task is shown, the field holds a new name.

Reading the task, recovering, and advancing do not start, complete, or cancel the task.
