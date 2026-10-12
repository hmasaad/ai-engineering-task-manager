# Contract: Requirement commands

New commands on the local API. A client-supplied engineer name or time is ignored. Extra fields are ignored. The wrong JSON shape, including a non-integer id, is 400 `The request is missing a required field or has the wrong shape.`

Stored results use `passed` and `failed`. The API shows Passed and Failed. Kinds are `functional` and `non-functional`.

## Record a requirement

`POST /api/requirements`

```json
{
  "statement": "The export contains the goal",
  "kind": "functional"
}
```

| Condition | Status | Message |
|---|---|---|
| `statement` is blank or only spaces. | 400 | `A requirement statement is required.` |
| `kind` is missing or is neither `functional` nor `non-functional`. | 400 | `Choose functional or non-functional.` |

Success is 200 and the requirement. The identifier is `REQ-` plus the new id. A blank statement is reported before an unknown kind.

## Read requirements

`GET /api/requirements` returns every requirement, oldest by id. Each item has `id`, `identifier`, `kind`, `statement`, and `missing`. `missing` is empty when the requirement has a task, a criterion, at least one active check, and a current Passed result for every active check. Otherwise it lists the phrases that apply, in this order:

- `Missing a task`
- `Missing an acceptance criterion`
- `Missing a check`
- `Missing a passing result for {check name}`

One passing phrase is included per active check that is not currently Passed, in check id order. The gap list is the items whose `missing` is not empty.

`GET /api/requirements/{id}` returns the requirement, or 404 `Requirement not found.`

```json
{
  "id": 1,
  "identifier": "REQ-1",
  "kind": "functional",
  "statement": "The export contains the goal",
  "tasks": [{"id": 1, "title": "Add export", "status": "In Progress"}],
  "criteria": [{"id": 2, "task_id": 1, "text": "The export contains the goal", "state": "Unverified"}],
  "checks": [
    {
      "id": 3,
      "name": "export shows the goal",
      "current_result": "Passed",
      "runs": [
        {
          "id": 4,
          "result": "Passed",
          "run_identifier": "local-1",
          "engineer_name": "Ada",
          "recorded_at": "2026-10-12T12:00:00Z"
        }
      ]
    }
  ],
  "removed_checks": []
}
```

`current_result` is `null` when the active check has no run. `removed_checks` use the same check shape and are not current. Runs are oldest first.

`GET /api/tasks/{id}` adds `requirements`. It is an empty list when none are linked to that task. Each item has `id`, `identifier`, `kind`, and `statement`.

## Change a requirement

`POST /api/requirements/{id}`

```json
{
  "statement": "The export contains the revised goal",
  "kind": "non-functional"
}
```

| Condition | Status | Message |
|---|---|---|
| The requirement id does not exist. | 404 | `Requirement not found.` |
| `statement` is blank or only spaces. | 400 | `A requirement statement is required.` |
| `kind` is missing or unknown. | 400 | `Choose functional or non-functional.` |

Success is 200 and the requirement. If the trimmed statement and the kind are unchanged, no criterion, task, or history row changes. A real change returns linked Verified criteria to Unverified. A Completed task that held one of those criteria is In Progress, its history includes `requirement_changed`, and Completed ancestors are In Progress too.

## Links

`POST /api/requirements/{id}/tasks`

```json
{ "task_id": 1 }
```

| Condition | Status | Message |
|---|---|---|
| The requirement id does not exist. | 404 | `Requirement not found.` |
| The task id does not exist. | 404 | `Task not found.` |

An existing pair returns 200 and writes no second row.

`POST /api/requirements/{id}/criteria`

```json
{ "task_id": 1, "criterion_id": 2 }
```

| Condition | Status | Message |
|---|---|---|
| The requirement id does not exist. | 404 | `Requirement not found.` |
| The task id does not exist. | 404 | `Task not found.` |
| The criterion id does not exist. | 404 | `Criterion not found.` |
| The criterion is not on that task, or the task is not linked. | 409 | `The criterion must be on that task.` |
| The pair is already stored. | 409 | `That criterion is already linked to this requirement.` |

`POST /api/requirements/{id}/tasks/{task_id}/unlink` and `POST /api/requirements/{id}/criteria/{criterion_id}/unlink` return 200 and the requirement. A missing requirement is 404 `Requirement not found.` A missing task or criterion link is 404 `Task not found.` or `Criterion not found.` Unlinking does not change Verified state and does not delete runs.

Deleting an acceptance criterion through the existing criterion command deletes the criterion link. The task link stays.

## Checks and runs

`POST /api/requirements/{id}/checks`

```json
{ "name": "export shows the goal" }
```

| Condition | Status | Message |
|---|---|---|
| The requirement id does not exist. | 404 | `Requirement not found.` |
| `name` is blank or only spaces. | 400 | `Name the check this requirement uses.` |
| That active name already exists on the requirement. | 409 | `That check is already named on this requirement.` |

`POST /api/requirements/{id}/checks/{check_id}/remove` returns 200. The check moves to `removed_checks` and its runs stay. An unknown or already removed check is 404 `Check not found.`

`POST /api/requirements/{id}/runs`

```json
{
  "check": "export shows the goal",
  "result": "Passed",
  "run_identifier": "local-1"
}
```

| Condition | Status | Message |
|---|---|---|
| The requirement id does not exist. | 404 | `Requirement not found.` |
| `check` is not an active name on that requirement. | 404 | `Check not found.` |
| `run_identifier` is blank or only spaces. | 400 | `A run identifier is required.` |
| `result` is missing or is neither Passed nor Failed. | 400 | `Choose Passed or Failed.` |

The requirement is checked before the check name, then the run identifier, then the result. Success is 200. The new run is last on that check. Task status and criterion state stay as they were.

## Existing commands this feature changes

`POST` verify on a criterion gains one refusal after the existing feature 001 checks: 409 `A required check has not passed.` A criterion with no linked requirement is unchanged.

`POST` complete gains a trailing sentence `A required check has not passed: REQ-1.` when a requirement linked to that task has an active check that is not currently Passed. Several identifiers are comma-separated, lowest number first. When older completion failures also apply, their sentences stay first. A task with no linked requirement keeps the message it has today.
