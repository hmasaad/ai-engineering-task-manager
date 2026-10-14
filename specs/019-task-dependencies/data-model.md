# Data Model: Task Dependencies

## Prerequisite link

One row for one task and one prerequisite.

| Field | Rule |
|---|---|
| `task_id` | Not null. References `task(id)`. Part of the primary key. |
| `prerequisite_id` | Not null. References `task(id)`. Part of the primary key. Must differ from `task_id`. |

No second row for the same pair. No update. The engineer can delete the row. Tasks are not deleted, so the row stays until the engineer removes the link.

The task payload adds `prerequisites`, ordered by prerequisite id. Each item has `id`, `title`, and `status`. It adds `blocked_by`, null when every prerequisite is Completed or there is no prerequisite. Otherwise it is the sentence in the contract.

## Execution order

Not stored. Derived from every task and every link. A prerequisite comes before the task that names it. Among tasks that could come next, the lower id comes first. The reading returns `id`, `title`, and `status` for every task.

## Unchanged

`task.status` stays Draft, Ready, In Progress, Completed, or Cancelled. A subtask row is not a prerequisite. Marking Ready, completing, and cancelling do not read this table, except that start reads it after the existing Ready check.
