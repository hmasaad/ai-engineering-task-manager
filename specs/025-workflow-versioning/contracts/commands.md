# Commands: Workflow Versioning and Migration

`GET /api/tasks` stays the top-level task list.

The workflow object on a task detail gains:

- `version`: the current version number, or `1` when steps exist and no version is stored yet. `null` when there are no steps.
- `draft`: `null`, or `{"number": 2, "steps": [ ... ]}` using the same step fields as `steps`.
- `migrations`: a list of `{"from_version": 1, "to_version": 2, "reason": "Replace the remaining step", "recorded_at": "..."}` in the order they were recorded.

## Revise

`POST /api/tasks/{id}/workflow/revise`

No body.

| Condition | Status | Result |
|---|---|---|
| The current version has a step that is no longer Pending, and no draft exists | 200 | The task detail. `draft.number` is the next version. Its steps are the ones that already left Pending. |
| No steps | 409 | `There is no workflow to revise.` |
| A step is Running | 409 | `Recover the interrupted step first.` |
| A draft exists | 409 | `A draft version already exists.` |
| Every step is Pending | 409 | `The workflow has not run yet.` |
| Unknown task | 404 | `Task not found.` |

The task status is unchanged. No step is performed.

The page button is `Revise workflow`. It is shown when the task is In Progress, the workflow has run, no step is interrupted, and no draft exists.

## Add and remove while a draft exists

`POST /api/tasks/{id}/workflow-steps` adds the new step to the draft. The current version's steps stay as they are.

Removing a draft step that is Pending removes it from the draft. Removing a draft step that is not Pending returns 409 `A step that already ran must stay in the new version.`

Without a draft, the existing add and remove rules stay in place.

## Migrate

`POST /api/tasks/{id}/workflow/migrate`

JSON body: `{"reason": "Replace the remaining step"}`. The page field is `migration-reason`. The button is `Migrate workflow`.

| Condition | Status | Result |
|---|---|---|
| A draft exists and the reason is not blank | 200 | The task detail. `version` is the draft number. `draft` is null. The migration is listed. |
| No draft | 409 | `There is no draft version to migrate.` |
| Blank reason | 400 | `Name why this workflow is migrating.` The draft stays. |
| A step is Running | 409 | `Recover the interrupted step first.` |
| The draft omits a step that already left Pending | 409 | `A step that already ran must stay in the new version.` |

The task status is unchanged. No step is performed. The replay is unchanged.

## Page

The workflow section shows `Version N` when a version is known. A draft shows `Draft version N` and its steps. After migration, the page shows the new version and `Version 1 superseded: Replace the remaining step`.
