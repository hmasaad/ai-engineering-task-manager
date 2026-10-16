# Data Model: Workflow Versioning and Migration

## workflow_version

One row is one version of one task. A new workspace creates the table. No column is added to an existing table.

| Column | Rule |
|---|---|
| `id` | New row |
| `task_id` | The task |
| `number` | 1 or greater. Unique for the task. |
| `state` | `Current`, `Draft`, or `Superseded` |

A task has at most one `Current` version and at most one `Draft` version.

## workflow_version_step

One row places one existing step on one version.

| Column | Rule |
|---|---|
| `version_id` | The version |
| `step_id` | The existing step |
| `position` | Order on that version, starting at 1. Unique for the version. |

The step row is not copied. A step that already ran can appear on the current version and on the draft.

## workflow_migration

One row is one migration.

| Column | Rule |
|---|---|
| `id` | New row |
| `task_id` | The task |
| `from_version_id` | The version that became superseded |
| `to_version_id` | The draft that became current |
| `reason` | Trimmed text, not empty |
| `recorded_at` | The workspace time |

## Task page

`GET /api/tasks` stays the top-level task list. The workflow on the task detail gains the current version number, the draft when one exists, and the migrations. A workflow with steps and no stored version reports version 1 without writing a row.
