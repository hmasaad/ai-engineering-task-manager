# Commands: Workflow Recovery and Replay

`GET /api/tasks` stays the top-level task list. Task detail `workflow` gains `replay` and `interrupted`.

## Replay

`GET /api/tasks/{task_id}/workflow-replay`

Success is 200 and `{"events": [...]}`. Each event has `id`, `step_id`, `title`, `state`, `detail`, and `recorded_at`, in `id` order. `detail` is null when the entry has none. An unknown task is 404 `Task not found.`

The task page lists the same entries under `Replay` when the list is not empty. Field container id: `workflow-replay`.

Reading the replay does not perform a step, add an entry, or change a status. It does not require the task to be In Progress.

## Advance

`POST /api/tasks/{task_id}/workflow/advance` keeps its current result when the first unfinished step is Pending, Failed, or Waiting.

When that step is Running, advance is 409 `Recover the interrupted step first.` The step stays Running and nothing is performed.

A completed advance still returns 200 and the task detail. The replay then contains a `Running` entry and the result entry.

## Recover

`POST /api/tasks/{task_id}/workflow/recover`

The page button is `Recover workflow`, shown while the task is In Progress and a step is Running. The advance button is hidden then.

| Condition | Status | Message |
|---|---|---|
| Unknown task | 404 | `Task not found.` |
| Draft task | 409 | `The task must be In Progress.` |
| Ready task | 409 | `Start the task first.` |
| Completed task | 409 | `Reopen the task first.` |
| Cancelled task | 409 | `A cancelled task cannot be changed. Continued work is a new task.` |
| No running step | 409 | `There is no step to recover.` |

A running step is 200 and the task detail.

- No newer effect: the step is Failed and `workflow.stopped` is `Stopped at {title}: the step was interrupted.`
- A newer file read: the step is Completed and the file is not read again.
- A newer folder change that is waiting: the step is Waiting and `workflow.stopped` is `Stopped at {title}: waiting for approval.`
- A newer folder change that was carried out: the step is Completed.

The following step stays Pending. The task status is unchanged. Recover does not approve a change.

Reading the replay, recovering, and advancing do not start, complete, or cancel the task.
