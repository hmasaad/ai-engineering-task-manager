# Data Model: Real Model

## model_service

One row for the workspace. A new workspace creates the table. No column is added to an existing table.

| Column | Rule |
|---|---|
| `id` | Always `1` |
| `model_name` | Trimmed text, not empty |
| `base_url` | Trimmed `http` or `https` address, not empty |
| `api_key` | Null when the engineer saves no key. Otherwise the key as entered, not empty after trimming |

Saving replaces that row. A blank name or a blank or unusable address leaves the row unchanged.

`configured_model` remains in the schema and is not read.

## Model reply

No new change column. The existing model record stores the prompt and the reply. The prompt includes the task title, the goal, the acceptance criteria, what changed, and the file text. The key is not in the prompt.

The reply is the text of the file to change. A new ordinary file is written with it. An existing file stays unchanged and the change waits for approval.

## Task page

`GET /api/tasks` stays the top-level task list. Task detail gains no new field. The model section of Instructions no longer has model text.
