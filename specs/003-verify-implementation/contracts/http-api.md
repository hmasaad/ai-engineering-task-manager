# Contract: Implementation check commands

These commands extend [the feature 002 command API](../../002-record-implementation/contracts/http-api.md). Common rules from that contract still apply: JSON bodies, trimmed text, server clock, localhost only, no authentication, and a refused command leaves every stored row unchanged.

The engineer stored on a check is the workspace engineer name. A client-supplied engineer name is ignored. A client-supplied time is ignored.

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
| 404 | The task id, the change id, or the criterion id does not exist. |
| 409 | The command is well-formed and the current status, outcome, or task link forbids it. |

## Task detail field

`GET /api/tasks/{id}` adds `checks` and `passing_check` on each object in `implementation_changes`. Feature 001 and feature 002 fields are otherwise unchanged. `checks` is oldest first.

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
  "passing_check": true,
  "checks": [
    {
      "id": 1,
      "criterion_id": 3,
      "criterion_text": "The export contains the goal",
      "evidence": "The detail page shows the goal in the export",
      "result": "Passed",
      "engineer_name": "Ada",
      "checked_at": "2026-10-07T12:05:00Z"
    }
  ]
}
```

`result` is `Passed` or `Failed`. `passing_check` is true only when the change is Carried out, at least one check names a criterion that still exists on that task, and every such criterion's latest check is `Passed`. It is false for a carried-out change that has no such check or has any current `Failed` result among those criteria. It is false for Awaiting approval and Not carried out. A check whose criterion no longer exists remains in `checks` and does not count toward `passing_check`.

## Record a check

`POST /api/tasks/{id}/implementation-changes/{change_id}/checks`

```json
{
  "criterion_id": 3,
  "evidence": "The detail page shows the goal in the export",
  "result": "Passed"
}
```

Success returns the task detail. The new check is the last item in that change's `checks`. The task status is unchanged. The change outcome is unchanged. The criterion's Verified state is unchanged.

| Case | Status | Message |
|---|---|---|
| Evidence empty or only spaces | 400 | `An account of the evidence is required.` |
| Result missing, or not `Passed` or `Failed` | 400 | `Choose Passed or Failed.` |
| Criterion id missing | 400 | `Choose an acceptance criterion.` |
| Body has the wrong shape | 400 | `The request is missing a required field or has the wrong shape.` |
| Unknown task id | 404 | `Task not found.` |
| Unknown change id | 404 | `Implementation change not found.` |
| Unknown criterion id | 404 | `Acceptance criterion not found.` |
| Task is Draft | 409 | `The task must be In Progress.` |
| Task is Ready | 409 | `Start the task first.` |
| Task is Completed | 409 | `Reopen the task first.` |
| Task is Cancelled | 409 | `A cancelled task cannot be changed. Continued work is a new task.` |
| Change exists on another task | 409 | `The check must name a change on that task.` |
| Criterion exists on another task | 409 | `The check must name a criterion on that task.` |
| Change is Awaiting approval | 409 | `The change must be carried out before it can be checked.` |
| Change is Not carried out | 409 | `A change that was not carried out cannot be checked.` |

A wrong task status is reported before a missing change, a blank body, or a bad result. Evidence is reported before a bad result when both are wrong. No row is written in any refused case.

## Complete

`POST /api/tasks/{id}/transitions` with `complete` keeps the feature 001 and feature 002 rules and adds this refusal.

While any carried-out change on this task lacks a passing check, the status stays `In Progress`, no status-change row is written, and the 409 message contains:

```text
Needs a passing check: {what_changed}
```

Several such changes are listed oldest first, separated by commas. When unverified criteria, unfinished subtasks, or changes Awaiting approval also block, their existing sentences remain, in that order, and this sentence follows them in the same message. When every carried-out change has a passing check, the feature 002 message is unchanged.

Not carried out changes do not add this sentence. A change that is Awaiting approval is named only in the awaiting-approval sentence. After every carried-out change on this task has a passing check, a completion that already meets the earlier guards succeeds.

## Cancel

`POST /api/tasks/{id}/transitions` with `cancel` is unchanged by this feature. A carried-out change that lacks a passing check does not add a sentence and does not refuse cancellation.

## Out of contract

These commands do not exist: edit a check, delete a check, move a check, send an engineer name, send a time, attach a file, run a test, or record a check as an assistant. Recording a check does not verify a criterion, approve a change, or record a decision.
