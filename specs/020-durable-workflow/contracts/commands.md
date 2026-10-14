# Commands: Durable Workflow Orchestration

`GET /api/tasks` stays the top-level task list. Task detail gains `workflow`.

## Add a step

`POST /api/tasks/{task_id}/workflow-steps`

Body: `title` (string, required), `action` (string), `project`, `path`, `what_changed`, and `class`. A missing title, or a title that is not a string, is the existing wrong-shape message. Extra fields are ignored. Blank optional strings are empty.

The page form posts those fields while the task is In Progress and no step has left Pending. Field ids: `step-title`, `step-action`, `step-project`, `step-path`, `step-what`, `step-class`. The action choices are `read` ("Read a file") and `folder` ("Create a folder"). The class choices are `ordinary` and `consequential`. A blank title shows `Name the step.` on the task page.

Success is 200 and the task detail. The new step is last and `Pending`.

Refusals, in order:

| Condition | Status | Message |
|---|---|---|
| Unknown task | 404 | `Task not found.` |
| Draft task | 409 | `The task must be In Progress.` |
| Ready task | 409 | `Start the task first.` |
| Completed task | 409 | `Reopen the task first.` |
| Cancelled task | 409 | `A cancelled task cannot be changed. Continued work is a new task.` |
| A step has left Pending | 409 | `A step can be added only before the workflow runs.` |
| Blank title | 400 | `Name the step.` |
| Blank or unknown action | 400 | `Choose a step action.` |
| Blank project | 400 | `Name the project this change is for.` |
| Read a file with a blank path | 400 | `Name the file this change reads.` |
| Create a folder with a blank account | 400 | `An account of what changed is required.` |
| Create a folder with a class other than ordinary or consequential | 400 | `Choose ordinary or consequential.` |
| Create a folder with a blank path | 400 | `Name the folder this change creates.` |

`what_changed` and `class` are ignored for Read a file.

## Remove a step

`POST /api/tasks/{task_id}/workflow-steps/{step_id}/remove`

The page button is `Remove step`, shown only while every step is Pending.

| Condition | Status | Message |
|---|---|---|
| Unknown task | 404 | `Task not found.` |
| Task not In Progress | 409 | The same status messages as add |
| A step has left Pending | 409 | `A step cannot be removed after the workflow runs.` |
| Step not on that task | 409 | `That step is not on this task.` |

Success is 200 and the task detail without that step.

## Advance

`POST /api/tasks/{task_id}/workflow/advance`

The page button is `Advance workflow`, shown while the task is In Progress, at least one step exists, and the workflow is not finished.

| Condition | Status | Message |
|---|---|---|
| Unknown task | 404 | `Task not found.` |
| Task not In Progress | 409 | The same status messages as add |
| No step, or every step Completed | 409 | `There is no step to run.` |

A step that is performed or settled is 200 and the task detail. `workflow.stopped` is the stop sentence, or null. `workflow.finished` is true only when every step is Completed. The task status is unchanged.

A Failed step uses `Stopped at {title}: {detail}` with the action message or the decline reason unchanged. A Waiting step uses `Stopped at {title}: waiting for approval.`

Adding a step, removing a step, advancing, and opening the task do not start, complete, or cancel the task.
