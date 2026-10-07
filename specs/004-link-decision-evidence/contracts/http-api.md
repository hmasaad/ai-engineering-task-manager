# Contract: Decisions that name a check

These commands extend [the feature 001 decision command](../../001-manage-engineering-tasks/contracts/http-api.md) and [the feature 003 task detail](../../003-verify-implementation/contracts/http-api.md). Common rules from those contracts still apply: JSON bodies, trimmed text, server clock, localhost only, no authentication, and a refused command leaves every stored row unchanged.

A client-supplied engineer name is ignored. A client-supplied time is ignored. The decision time is the server clock. The engineer and time shown for the named check are the ones already stored on that check.

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
| 404 | The task id, the check id, or a superseded decision id does not exist. |
| 409 | The command is well-formed and the current status or task link forbids it. |

## Task detail field

`GET /api/tasks/{id}` adds `check` on each object in `decisions`. Feature 001, feature 002, and feature 003 fields are otherwise unchanged. `decisions` stays oldest first.

A decision that names no check:

```json
{
  "id": 4,
  "statement": "Use one file",
  "rationale": "One engineer has one workspace",
  "recorded_at": "2026-10-07T12:00:00Z",
  "supersedes": [],
  "check": null
}
```

A decision that names a check:

```json
{
  "id": 5,
  "statement": "Keep the export label",
  "rationale": "The check shows the goal is visible",
  "recorded_at": "2026-10-07T12:06:00Z",
  "supersedes": [4],
  "check": {
    "id": 1,
    "change_id": 7,
    "what_changed": "Rename the export label",
    "criterion_id": 3,
    "criterion_text": "The export contains the goal",
    "evidence": "The detail page shows the goal in the export",
    "result": "Passed",
    "engineer_name": "Ada",
    "checked_at": "2026-10-07T12:05:00Z"
  }
}
```

`result` is `Passed` or `Failed`. `check` is the named check, not the latest check of that change and criterion. A later check does not change `check.id`, `evidence`, or `result` on this decision.

## Record a decision that names a check

`POST /api/tasks/{id}/linked-decisions`

```json
{
  "statement": "Keep the export label",
  "rationale": "The check shows the goal is visible",
  "check_id": 1,
  "supersedes": [4]
}
```

`supersedes` may be omitted or empty. Success returns the task detail. The new decision is the last item in `decisions`. Its `check.id` is the named check. The task status is unchanged. The change outcome is unchanged. The check's evidence and result are unchanged. The criterion's Verified state is unchanged.

| Case | Status | Message |
|---|---|---|
| Statement or rationale empty or only spaces | 400 | `Both a statement and a rationale are required.` |
| Check id missing | 400 | `Choose the check this decision rests on.` |
| Body has the wrong shape | 400 | `The request is missing a required field or has the wrong shape.` |
| Unknown task id | 404 | `Task not found.` |
| Unknown check id | 404 | `Check not found.` |
| Unknown decision id in `supersedes` | 404 | `Decision not found.` |
| Task is Cancelled | 409 | `Decisions cannot be added to a cancelled task.` |
| Check exists on another task | 409 | `The decision must name a check on that task.` |
| Superseded decision exists on another task | 409 | `A decision can only supersede earlier decisions on the same task.` |
| Superseded decision is this decision or a later one | 409 | `A decision cannot supersede itself or a decision that comes after it.` |

A Cancelled task is reported before a blank statement or a missing check. A blank statement or rationale is reported before a missing, unknown, or wrong-task check. No row is written in any refused case.

Draft, Ready, In Progress, and Completed are not refused by status when the named check is on that task. Passed and Failed are both accepted. The named check does not have to be the current result of its change and criterion.

## Existing decision command

`POST /api/tasks/{id}/decisions` is unchanged. It still saves a decision with a statement and a rationale and no check. `check` on that decision is null. A `check_id` in that body is ignored. It does not link the decision and it does not refuse the command.

## Complete and cancel

`POST /api/tasks/{id}/transitions` with `complete` or `cancel` is unchanged by this feature. A carried-out change with no decision does not add a sentence and does not refuse either command.

## Out of contract

These commands do not exist: edit a decision, delete a decision, move a decision to another check, send an engineer name, send a time, attach a file, or record a decision as an assistant. Recording this decision does not verify a criterion, record a check, approve a change, or change task status.
