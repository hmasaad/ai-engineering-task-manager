# Contract: Assistant change commands

These commands extend [the feature 002 command API](../../002-record-implementation/contracts/http-api.md) and [the feature 004 task detail](../../004-link-decision-evidence/contracts/http-api.md). Common rules from those contracts still apply: JSON bodies, trimmed text, server clock, localhost only, no authentication, and a refused command leaves every stored row unchanged.

The assistant stored on an assistant change is the configured assistant name. A client-supplied assistant name is ignored. A client-supplied engineer name is ignored. A client-supplied time is ignored. `engineer_name` on the change remains the workspace engineer.

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
| 404 | The task id does not exist. |
| 409 | The command is well-formed and the current status or actor forbids it. |

## Task detail field

`GET /api/tasks/{id}` adds `project`, `assistant_name`, `recorded_by`, and `stopped` on each object in `implementation_changes`. Feature 001 through feature 004 fields are otherwise unchanged. `implementation_changes` stays oldest first.

An engineer change:

```json
{
  "id": 7,
  "what_changed": "Rename the export label",
  "class": "ordinary",
  "outcome": "Carried out",
  "engineer_name": "Ada",
  "recorded_at": "2026-10-07T12:00:00Z",
  "approval": null,
  "not_carried_out": null,
  "project": null,
  "assistant_name": null,
  "recorded_by": "engineer",
  "stopped": false
}
```

An ordinary assistant change:

```json
{
  "id": 8,
  "what_changed": "Rename the export label",
  "class": "ordinary",
  "outcome": "Carried out",
  "engineer_name": "Ada",
  "recorded_at": "2026-10-07T12:05:00Z",
  "approval": null,
  "not_carried_out": null,
  "project": "billing",
  "assistant_name": "Guide",
  "recorded_by": "assistant",
  "stopped": false
}
```

`recorded_by` is `assistant` or `engineer`. `stopped` is true only when an ordinary request was stored as `consequential` because the assistant stopped. `class` is then `consequential` and `outcome` is `Awaiting approval`.

## Record an assistant change

`POST /api/tasks/{id}/assistant-changes`

```json
{
  "project": "billing",
  "class": "ordinary",
  "what_changed": "Rename the export label",
  "stopped": false
}
```

`stopped` may be omitted. It defaults to false. `class` is `ordinary` or `consequential`.

Success returns the task detail. The new change is the last item in `implementation_changes`. The task status is unchanged. No check and no decision are added.

| Request | Stored outcome |
|---|---|
| `class` `ordinary` and `stopped` false | Carried out, `stopped` false |
| `class` `consequential` | Awaiting approval, `stopped` false |
| `class` `ordinary` and `stopped` true | Awaiting approval, `class` `consequential`, `stopped` true |

| Case | Status | Message |
|---|---|---|
| Project empty or only spaces | 400 | `Name the project this change is for.` |
| Account of what changed empty or only spaces | 400 | `An account of what changed is required.` |
| Class missing, or not `ordinary` or `consequential` | 400 | `Choose ordinary or consequential.` |
| Body has the wrong shape | 400 | `The request is missing a required field or has the wrong shape.` |
| Unknown task id | 404 | `Task not found.` |
| Task is Draft | 409 | `The task must be In Progress.` |
| Task is Ready | 409 | `Start the task first.` |
| Task is Completed | 409 | `Reopen the task first.` |
| Task is Cancelled | 409 | `A cancelled task cannot be changed. Continued work is a new task.` |

A wrong task status is reported before a blank project or a blank account. A blank project is reported before a blank account. A blank account is reported before a bad class. No row is written in any refused case.

This command does not open or write the named project.

## Existing change command

`POST /api/tasks/{id}/implementation-changes` is unchanged. It still saves the engineer's change. `recorded_by` is `engineer`, and `project` and `assistant_name` are null. A `project` or `assistant_name` in that body is ignored.

## Approve and decline

`POST /api/tasks/{id}/implementation-changes/{change_id}/approve` and `POST /api/tasks/{id}/implementation-changes/{change_id}/not-carried-out` keep the feature 002 rules when `actor` is omitted.

| Case | Status | Message |
|---|---|---|
| Approve with `actor` `assistant` | 409 | `The assistant cannot approve a change.` |
| Decline with `actor` `assistant` | 409 | `The assistant cannot decline a change.` |

The change stays as it was. No resolution row is written. An approval that succeeds still names the workspace engineer in `approval.engineer_name`.

## Complete and cancel

`POST /api/tasks/{id}/transitions` with `complete` or `cancel` is unchanged by this feature. A carried-out assistant change still needs a passing check before completion. A waiting assistant change still blocks completion and cancellation.

## Out of contract

These commands do not exist: edit an assistant change, delete an assistant change, call a model, write the named project, send an assistant name, send a time, record a check as the assistant, record a decision as the assistant, or complete a task as the assistant.
