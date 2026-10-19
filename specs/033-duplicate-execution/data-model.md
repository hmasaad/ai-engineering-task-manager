# Data Model: Idempotency and Duplicate Execution Control

## command_execution

One row records one accepted Read a file or Create a folder for one name on one task. A new workspace creates the table. No column is added to an existing table.

| Column | Rule |
|---|---|
| `id` | New row |
| `task_id` | The task |
| `name` | The trimmed execution name. One row for that name on that task |
| `action` | `read` or `folder` |
| `path` | The file or folder path the command stored, trimmed, not empty |
| `recorded_at` | The time the command was accepted |

A second insert for the same task and name does not add a row. A refused command and a rolled-back command have no row. A blank name has no row. A workflow step has no row.

## Task detail

`GET /api/tasks` stays the top-level task list. The task detail gains `executions`.

| Field | Rule |
|---|---|
| `name` | The trimmed name |
| `action` | `read` or `folder` |
| `path` | The path stored with that execution |

The list is oldest first. It is empty when no named execution is stored.
