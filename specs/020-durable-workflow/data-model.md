# Data Model: Durable Workflow Orchestration

## workflow_step

One row is one step on one task.

| Column | Rule |
|---|---|
| `id` | Integer primary key |
| `task_id` | References `task(id)` |
| `position` | Integer, unique with `task_id`, assigned as one more than the current maximum, starting at 1 |
| `title` | Trimmed, non-empty |
| `action` | `read` or `folder` |
| `project` | Trimmed, non-empty |
| `path` | Trimmed, non-empty. A file path for `read`. A folder path for `folder` |
| `what_changed` | Null for `read`. Required for `folder` |
| `change_class` | Null for `read`. `ordinary` or `consequential` for `folder` |
| `state` | `Pending`, `Completed`, `Waiting`, or `Failed` |
| `detail` | Null, or the action message, or the decline reason |
| `change_id` | Null, or the implementation change a folder step recorded |

Index: unique `(task_id, position)`.

A `read` row has null `what_changed` and null `change_class`. A `folder` row has both set. `state` starts as `Pending`.

## Task detail

`workflow` is always present:

| Field | Rule |
|---|---|
| `steps` | Each step as `id`, `title`, `action`, `state`, `project`, `path`, and `change_id`, in `position` order |
| `stopped` | Null, or `Stopped at {title}: {detail}` for the first Failed step, or `Stopped at {title}: waiting for approval.` for the first Waiting step. A Pending step before those clears it |
| `started` | True when any step is not Pending |
| `finished` | True when there is at least one step and every step is Completed |

`GET /api/tasks` does not include `workflow`.

## State changes

- Add inserts one `Pending` row. Remove deletes one row. Neither runs after any row for that task has left `Pending`.
- Advance selects the lowest `position` whose `state` is not `Completed`.
- `Pending` or `Failed` calls the existing action. A Refusal sets `Failed` and `detail` to that message. A read that succeeds sets `Completed`. A folder whose new change is Carried out sets `Completed` and `change_id`. A folder whose new change is Awaiting approval sets `Waiting` and `change_id`.
- `Waiting` does not call the action. The stored change decides Completed, Failed, or leaving it Waiting.
- Task `status` is not written by these commands.
