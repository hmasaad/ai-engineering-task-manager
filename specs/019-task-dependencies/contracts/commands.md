# Commands: Task Dependencies

`GET /api/tasks` stays the top-level task list. Task detail gains `prerequisites` and `blocked_by`.

## Add a prerequisite

`POST /api/tasks/{task_id}/prerequisites`

Body: `prerequisite_id` (integer). A missing or non-integer id is the existing wrong-shape message. Extra fields are ignored.

The page form posts `prerequisite_id` while the task is not Cancelled. Field id: `prerequisite-id`. A blank value shows `Name the prerequisite task.` on the task page.

Success is 200 and the task detail. The prerequisite is listed once.

Refusals, in order:

| Condition | Status | Message |
|---|---|---|
| Unknown task | 404 | `Task not found.` |
| Cancelled task | 409 | `A cancelled task cannot be changed. Continued work is a new task.` |
| Blank id on the page | the task page | `Name the prerequisite task.` |
| Unknown prerequisite | 404 | `Prerequisite not found.` |
| Same task | 409 | `A task cannot depend on itself.` |
| Cycle | 409 | `That dependency would form a cycle.` |

A repeated link is 200 and does not add a second row.

## Remove a prerequisite

`POST /api/tasks/{task_id}/prerequisites/{prerequisite_id}/remove`

The page button is `Remove prerequisite`.

| Condition | Status | Message |
|---|---|---|
| Unknown task | 404 | `Task not found.` |
| Cancelled task | 409 | `A cancelled task cannot be changed. Continued work is a new task.` |
| Unknown prerequisite | 404 | `Prerequisite not found.` |
| Not linked | 409 | `That prerequisite is not linked.` |

Success is 200 and the task detail without that prerequisite. Neither status changes.

## Execution order

`GET /api/execution-order`

Success is 200, a list of `{id, title, status}` for every task. Each prerequisite comes first. The lower id comes first when several tasks could be next. The task list page shows the same list under `Execution order` when it is not empty.

## Start

`POST /api/tasks/{task_id}/transitions` with `action` `start` keeps the current refusal when the task is not Ready: 409 `The task must be Ready to start work.`

When the task is Ready and a prerequisite is not Completed, start is 409 and the task stays Ready. Prerequisites are named from the lowest id:

- `Blocked by {title} ({status}): unverified {criteria}.` when that prerequisite has an unverified criterion. Criteria are listed in their stored order, separated by a comma and a space.
- `Blocked by {title} ({status}): incomplete.` otherwise.

Several prerequisites are joined in that order with `. ` and a final period.

The task page shows `blocked_by` under Status while it is set.

Adding a link, removing a link, and reading the order do not start, complete, or cancel a task.
