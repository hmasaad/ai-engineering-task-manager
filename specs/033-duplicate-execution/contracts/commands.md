# Commands: Idempotency and Duplicate Execution Control

`GET /api/tasks` stays the top-level task list.

The task detail gains `executions`: `{name, action, path}` oldest first. `action` is `read` or `folder`.

## Read a file

`POST /api/tasks/{id}/file-reads`

The body gains an optional `execution` string. A missing or blank value is not saved. The page field is Execution name, id `read-execution`, name `execution`.

| Condition | Status | Result |
|---|---|---|
| First accepted use of the name | 200 | One file read, and one execution with `action` `read` and that path |
| Same name again | 200 | The earlier file read and execution. The file is not read again |
| Blank name | 200 | The existing read rules. No execution is added |
| Missing file, and the name is new | 400 | `The file must already exist.` The name is not saved |
| Task is not In Progress | 409 | `The task must be In Progress.` The name is not saved |
| Unknown task | 404 | `Task not found.` |

## Create a folder

`POST /api/tasks/{id}/folders`

The body gains the same optional `execution` string. The page field is Execution name, id `folder-execution`, name `execution`.

| Condition | Status | Result |
|---|---|---|
| First accepted use of the name | 200 | One folder change, and one execution with `action` `folder` and that path |
| Same name again | 200 | The earlier folder change and execution. The folder is not created again |
| Blank name | 200 | The existing folder rules. No execution is added |
| The command is refused, and the name is new | 400 or 409 | The existing refusal. The name is not saved |

A repeated name does not approve a change and does not advance a workflow.

## Page

The task shows Executions. Each item names the execution, Read a file or Create a folder, and the path. When none are stored, the page says `No named executions yet.` The list id is `command-executions`.
