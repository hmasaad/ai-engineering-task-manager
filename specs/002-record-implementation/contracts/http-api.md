# Contract: Implementation change commands

These commands extend [the feature 001 command API](../../001-manage-engineering-tasks/contracts/http-api.md). Common rules from that contract still apply: JSON bodies, trimmed text, server clock, localhost only, no authentication, and a refused command leaves every stored row unchanged.

The provider stored on a change or a resolution is the workspace engineer name. A client-supplied engineer name is ignored.

## Error body

Same shape as feature 001:

```json
{
  "refused": true,
  "message": "Human-readable explanation of what is missing or illegal."
}
```

| Status | When |
|---|---|
| 400 | A required field is missing, blank, or the wrong shape. |
| 404 | The task id or the change id does not exist. |
| 409 | The command is well-formed and the current status, outcome, or task link forbids it. |

## Task detail field

`GET /api/tasks/{id}` adds `implementation_changes`, oldest first. Feature 001 fields are unchanged.

Ordinary change:

```json
{
  "id": 7,
  "what_changed": "Rename the export label",
  "class": "ordinary",
  "outcome": "Carried out",
  "engineer_name": "Ada",
  "recorded_at": "2026-10-07T12:00:00Z",
  "approval": null,
  "not_carried_out": null
}
```

Consequential change that is Awaiting approval has `"outcome": "Awaiting approval"` and both `approval` and `not_carried_out` null.

Carried-out consequential change:

```json
{
  "outcome": "Carried out",
  "approval": {
    "evidence": "The export label on the detail page reads Export.",
    "engineer_name": "Ada",
    "approved_at": "2026-10-07T12:10:00Z"
  },
  "not_carried_out": null
}
```

Not carried out:

```json
{
  "outcome": "Not carried out",
  "approval": null,
  "not_carried_out": {
    "reason": "The label change was the wrong fix.",
    "engineer_name": "Ada",
    "declined_at": "2026-10-07T12:12:00Z"
  }
}
```

`class` is `ordinary` or `consequential`. `outcome` is `Carried out`, `Awaiting approval`, or `Not carried out`.

## Record a change

`POST /api/tasks/{id}/implementation-changes`

```json
{
  "what_changed": "Rename the export label",
  "class": "ordinary"
}
```

`class` must be `ordinary` or `consequential`. Success returns the task detail. The task status is unchanged. No criterion, history, or decision row is written.

| Condition | Status | Message |
|---|---|---|
| Blank `what_changed` | 400 | `An account of what changed is required.` |
| Missing or unknown `class` | 400 | `Choose ordinary or consequential.` |
| Task is Draft | 409 | `The task must be In Progress.` |
| Task is Ready | 409 | `Start the task first.` |
| Task is Completed | 409 | `Reopen the task first.` |
| Task is Cancelled | 409 | `A cancelled task cannot be changed. Continued work is a new task.` |
| Unknown task id | 404 | `Task not found.` |

An ordinary change is stored as Carried out. A consequential change is stored as Awaiting approval and has no approval.

## Approve a change

`POST /api/tasks/{id}/implementation-changes/{change_id}/approve`

```json
{
  "evidence": "The export label on the detail page reads Export."
}
```

Success returns the task detail. That change is Carried out, the approval names the evidence, the workspace engineer, and the server time, and the task status is unchanged.

| Condition | Status | Message |
|---|---|---|
| Blank `evidence` | 400 | `An account of the evidence reviewed is required.` |
| Ordinary change | 409 | `An ordinary change does not wait for approval.` |
| Already Carried out consequential change | 409 | `The change is already carried out.` |
| Not carried out | 409 | `It cannot be carried out.` |
| Task is not In Progress | 409 | `The task must be In Progress.` |
| Change exists on another task | 409 | `The approval must name a change on that task.` |
| Unknown change id | 404 | `Implementation change not found.` |
| Unknown task id | 404 | `Task not found.` |

Saving the change is not this command. There is no approve flag on record.

## Mark a change not carried out

`POST /api/tasks/{id}/implementation-changes/{change_id}/not-carried-out`

```json
{
  "reason": "The label change was the wrong fix."
}
```

Success returns the task detail. That change is Not carried out and stays visible. The task status is unchanged. It cannot be approved afterward.

| Condition | Status | Message |
|---|---|---|
| Blank `reason` | 400 | `A reason is required.` |
| Change is Carried out | 409 | `A carried-out change stays in the record.` |
| Change is already Not carried out | 409 | `It cannot be carried out.` |
| Task is not In Progress | 409 | `The task must be In Progress.` |
| Change exists on another task | 409 | `The change must be on that task.` |
| Unknown change id | 404 | `Implementation change not found.` |

## Complete and cancel

`POST /api/tasks/{id}/transitions` with `complete` or `cancel` keeps the feature 001 rules and adds this refusal.

While any change on this task is Awaiting approval, the status stays `In Progress`, no status-change row is written, and the 409 message contains:

```text
Awaiting approval: {what_changed}
```

Several waiting changes are listed oldest first, separated by commas. When unverified criteria or unfinished subtasks also block, their existing sentences remain, and this sentence is included in the same message. When nothing is Awaiting approval, the feature 001 message is unchanged.

Carried out and Not carried out changes do not add this sentence. After every waiting change on this task is approved or marked not carried out, a completion that already meets the feature 001 guards succeeds.

## Out of contract

These commands do not exist: edit a change, delete a change, delete a resolution, move a change to another task, send an engineer name, attach a file or a review link, or record a change as an assistant. Recording a decision does not create a change. Recording a change does not create a decision.
