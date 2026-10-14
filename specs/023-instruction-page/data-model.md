# Data Model: Instruction Page

## configured_model

One row for the workspace. A new workspace creates the table. No column is added to an existing table.

| Column | Rule |
|---|---|
| `id` | Always `1` |
| `model_name` | Trimmed text, not empty |
| `model_text` | The text the model returns. Not empty after trimming. Stored as entered, including a trailing line break |

Saving replaces that row. A blank name or blank text leaves the row unchanged.

## Instruction

No table. Starting work creates the existing task, goal, acceptance criterion, file read, and model proposal.

The task status becomes In Progress. The model is asked once. A new ordinary file is written. An existing file stays unchanged and the change waits for approval.

## Task page

`GET /api/tasks` stays the top-level task list. Task detail gains no new field.
