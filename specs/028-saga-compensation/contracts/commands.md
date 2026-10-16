# Commands: Saga Pattern and Compensation

`GET /api/tasks` stays the top-level task list.

The workflow object on a task detail gains `saga` and `compensations`.

## Compensate

`POST /api/tasks/{id}/workflow/compensate`

JSON body: `{"reason": "Withdraw the note"}`. The page field is `compensation-reason`. The button is `Compensate`.

| Condition | Status | Result |
|---|---|---|
| A step has failed, a completed step has no compensation, and the reason is not blank | 200 | The task detail. A file read is `Compensated`. A folder is `Waiting` and the folder remains. |
| The workflow has not failed | 409 | `The workflow has not failed.` |
| A step is running | 409 | `Recover the interrupted step first.` |
| A compensation is waiting | 409 | `Finish the waiting compensation first.` |
| No completed step remains | 409 | `There is no step to compensate.` |
| Blank reason | 400 | `Name why this step is compensated.` |
| Unknown task | 404 | `Task not found.` |

The latest completed step without a compensation is the one withdrawn. The task status is unchanged. A file read remains stored.

## Approve

`POST /api/tasks/{id}/workflow/compensations/{compensation_id}/approve`

JSON body: `{"evidence": "The folder is empty"}`. The page field is `compensation-evidence-{id}`. The button is `Approve compensation`.

| Condition | Status | Result |
|---|---|---|
| The compensation is waiting, the evidence is not blank, and the folder is empty or already gone | 200 | The compensation is `Compensated`. An empty folder is removed. The original change remains. |
| Blank evidence | 400 | `An account of the evidence reviewed is required.` |
| The folder contains something | 409 | `The folder must be empty to compensate.` The folder remains. |
| The compensation is not waiting | 409 | `That compensation is not waiting.` |
| The compensation is not on the task | 409 | `That compensation is not on this task.` |

## Mark not carried out

`POST /api/tasks/{id}/workflow/compensations/{compensation_id}/decline`

JSON body: `{"reason": "Keep the folder"}`. The page field is `compensation-decline-{id}`. The button is `Mark compensation not carried out`.

| Condition | Status | Result |
|---|---|---|
| The compensation is waiting and the reason is not blank | 200 | The compensation is `Not carried out`. The folder remains. |
| Blank reason | 400 | `Name why this compensation will not be carried out.` |

## Page

The workflow section shows `Saga Open`, `Saga Failed`, `Saga Waiting`, or `Saga Compensated`. Compensate is shown when the saga is Failed and the task is In Progress. A waiting compensation shows the approval and the decline forms.
