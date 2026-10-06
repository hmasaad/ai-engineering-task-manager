# Contract: Local command API

The UI and automated tests call these commands. Each command runs one domain operation from `data-model.md`. The server listens on `127.0.0.1` only. There is no authentication. The provider stored on a verification is the workspace engineer name, never a name sent by the client.

## Common rules

- Request and response bodies are JSON.
- Text fields are trimmed. Empty or whitespace-only values fail as a validation error.
- A refused command returns the error body below and leaves every stored row unchanged.
- Times are assigned by the server clock (the test clock in tests), not by the client.
- Lists are ordered as the data model specifies: oldest first.

### Error body

```json
{
  "refused": true,
  "message": "Human-readable explanation of what is missing or illegal."
}
```

| Status | When |
|---|---|
| 400 | A required field is missing, blank, or the wrong shape. |
| 404 | The task, criterion, or decision id does not exist. |
| 409 | The command is well-formed and the current status or links forbid it. Completion refusals name each Unverified criterion and each unfinished subtask. |

### Success body

Mutating commands return the task detail below. List and read commands return the list or the detail.

## Task detail

```json
{
  "id": 1,
  "title": "Add export",
  "goal": "An engineer can take a finished task record with them",
  "status": "In Progress",
  "parent_id": null,
  "created_at": "2026-10-06T12:00:00Z",
  "cancel_reason": null,
  "criteria": [],
  "subtasks": [],
  "decisions": [],
  "history": []
}
```

Criterion when Unverified: `observation`, `pass_result`, `verified_at`, and `provider_name` are `null`.

Criterion when Verified:

```json
{
  "id": 10,
  "text": "The export contains the goal",
  "state": "Verified",
  "observation": "The file included the goal sentence.",
  "pass_result": "pass",
  "verified_at": "2026-10-06T12:05:00Z",
  "provider_name": "Engineer"
}
```

History entry:

```json
{
  "id": 3,
  "from_status": "Ready",
  "to_status": "In Progress",
  "occurred_at": "2026-10-06T12:04:00Z",
  "cause_code": "started",
  "cause_detail": null
}
```

Decision:

```json
{
  "id": 4,
  "statement": "Store the workspace in one file",
  "rationale": "One engineer has one workspace",
  "recorded_at": "2026-10-06T12:06:00Z",
  "supersedes": [2, 3]
}
```

Subtask summaries on a parent are `{id, title, status, created_at}` in creation order. The full detail is loaded by reading that id.

## Commands

### List top-level tasks

`GET /api/tasks`

Returns an array of `{id, title, status, created_at}` for tasks with no parent.

### Create a task

`POST /api/tasks`

```json
{ "title": "Add export" }
```

Result: status `Draft`, no parent. Blank title is 400 and creates nothing.

### Read a task

`GET /api/tasks/{id}`

Returns the task detail. Unknown id is 404.

### Set the goal

`PATCH /api/tasks/{id}`

```json
{ "goal": "An engineer can take a finished task record with them" }
```

Refused with 409 when the task is `Cancelled`, or when the goal is cleared while the task is `In Progress` or `Completed`. Clearing the goal of a `Ready` task returns it to `Draft` and appends a `goal_or_last_criterion_removed` history row.

### Add a criterion

`POST /api/tasks/{id}/criteria`

```json
{ "text": "The export contains the goal" }
```

The new criterion is Unverified. Refused with 409 on a Cancelled task.

### Edit a criterion

`PATCH /api/tasks/{id}/criteria/{criterion_id}`

```json
{ "text": "The export contains the goal and the status" }
```

If the criterion was Verified, it becomes Unverified and its observation, pass result, time, and provider are cleared. If the task was `Completed`, it becomes `In Progress` and every Completed ancestor becomes `In Progress`. Those history rows use `criterion_text_edited` and the criterion id. Refused with 409 on a Cancelled task.

### Remove a criterion

`DELETE /api/tasks/{id}/criteria/{criterion_id}`

Refused with 409 when this is the last criterion and the task is `In Progress` or `Completed`, or when the task is `Cancelled`. Removing the last criterion of a `Ready` task returns that task to `Draft`.

### Verify a criterion

`POST /api/tasks/{id}/criteria/{criterion_id}/verify`

```json
{
  "observation": "The file included the goal sentence.",
  "pass_result": "pass"
}
```

Allowed only while the task is `In Progress`. Stores the observation, pass, the server time, and the workspace engineer name. `pass_result` other than `pass`, or a blank observation, is 400 and leaves the criterion Unverified. The client cannot send a provider name.

### Unverify a criterion

`POST /api/tasks/{id}/criteria/{criterion_id}/unverify`

Allowed only while the task is `In Progress`. Clears observation, pass result, time, and provider. The task status does not change.

### Change status

`POST /api/tasks/{id}/transitions`

```json
{ "action": "mark_ready" }
```

| action | Extra field | From |
|---|---|---|
| `mark_ready` | none | Draft, and the ready guard holds |
| `start` | none | Ready |
| `complete` | none | In Progress, and the completion guard holds |
| `cancel` | `reason` non-empty | Draft, Ready, or In Progress, and every direct subtask is Completed or Cancelled |
| `reopen` | `reason` non-empty | Completed. Also moves Completed ancestors to In Progress |

Any other action, or a legal action from the wrong status, is 409. `cancel` and `reopen` without a reason are 400. Reopen does not clear verifications.

### Add a subtask

`POST /api/tasks/{id}/subtasks`

```json
{ "title": "Write the checklist" }
```

Creates a Draft task whose parent is `{id}`. Refused with 409 when the parent is Completed or Cancelled, or when `{id}` would become its own ancestor. The parent link is set only here. There is no command to move a task under a different parent.

### Record a decision

`POST /api/tasks/{id}/decisions`

```json
{
  "statement": "Store the workspace in one file",
  "rationale": "One engineer has one workspace",
  "supersedes": [2, 3]
}
```

`supersedes` may be omitted or empty. Each id must be an earlier decision on this same task. A self id, a later id, or another task's id is 409 and saves nothing. Blank statement or rationale is 400. Refused with 409 on a Cancelled task. There is no update or delete command for a decision.

## Out of contract

These commands do not exist in this feature: delete a task, delete a decision, restore a Cancelled task, sign in, assign another person, or submit a verification as an assistant.
