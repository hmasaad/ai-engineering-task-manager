# Commands: Workflow Snapshots and Checkpointing

`GET /api/tasks` stays the top-level task list.

The workflow object on a task detail gains `checkpoints`.

## Take a checkpoint

`POST /api/tasks/{id}/workflow/checkpoints`

JSON body: `{"name": "before the read"}`. The page field is `checkpoint-name`. The button is `Take checkpoint`.

| Condition | Status | Result |
|---|---|---|
| The task has steps, none is running, and the name is new | 200 | The task detail. The checkpoint lists each current step and its state. |
| The same name was already taken on this task | 200 | The task detail. The original snapshot is unchanged. |
| Blank name | 400 | `Name this checkpoint.` |
| No steps | 409 | `There is no workflow to checkpoint.` |
| A step is running | 409 | `Recover the interrupted step first.` |
| Unknown task | 404 | `Task not found.` |

## Restore

`POST /api/tasks/{id}/workflow/checkpoints/{checkpoint_id}/restore`

No body. The button is `Restore checkpoint`.

| Condition | Status | Result |
|---|---|---|
| The checkpoint's steps are the current steps, and a failed step was Pending in the snapshot and has no stored effect | 200 | That step is Pending. A completed step stays completed. |
| A failed step has a stored effect | 409 | `A stored effect cannot be restored over.` The step stays failed. |
| The current steps differ from the snapshot | 409 | `The workflow has changed since this checkpoint.` |
| The checkpoint is not on the task | 409 | `That checkpoint is not on this task.` |
| A step is running | 409 | `Recover the interrupted step first.` |

## Read

`GET /api/tasks/{id}/workflow/checkpoints`

The read writes nothing and does not call the clock. No checkpoints returns `{"checkpoints": []}`. An unknown task is `Task not found.`

## Page

The workflow section says `No checkpoints yet.` when none exist. Otherwise it lists each checkpoint, its step states, and Restore checkpoint. Take checkpoint is shown when the task is In Progress, steps exist, and no step is running.
