# Data Model: Autoscaling and Queue-Based Capacity Planning

## Waiting work

One named item that no worker holds yet.

| Field | Rule |
|---|---|
| `id` | Integer. Assigned when the item is queued. The smaller id is the older item. |
| `task_id` | The task. Required. |
| `name` | Trimmed text. Required. Unique on the task. |
| `job_id` | Empty while the item is waiting. Set to the job when a scale assigns it. |
| `recorded_at` | The workspace time when the item was queued. Required. |

A second insert for the same task and name does not add a row.

## Capacity plan

One named reading.

| Field | Rule |
|---|---|
| `id` | Integer. Assigned when the plan is stored. |
| `task_id` | The task. Required. |
| `name` | Trimmed text. Required. Unique on the task. |
| `waiting` | Waiting items at that time. Zero or more. |
| `held` | Jobs held by active workers at that time. Zero or more. |
| `active` | Active workers at that time. Zero or more. |
| `needed` | Workers needed at that time. Zero when `waiting + held` is zero. Otherwise one worker for every three items, rounded up. |
| `recorded_at` | The workspace time when the plan was stored. Required. |

## Scale

One named change.

| Field | Rule |
|---|---|
| `id` | Integer. Assigned when the scale is stored. |
| `task_id` | The task. Required. |
| `name` | Trimmed text. Required. Unique on the task. |
| `direction` | `fill`, `up`, or `down`. |
| `worker_id` | The worker who received the item, the worker who was added, or the worker who was released. Required. |
| `job_id` | The job assigned by a fill or a scale-up. Empty for a release. |
| `recorded_at` | The workspace time when the scale was stored. Required. |

A fill or a scale-up sets the waiting item's `job_id` in the same transaction. A scale-up also inserts the worker. A release inserts one `work_release` row for that worker in the same transaction.

## Release

One active worker who was released.

| Field | Rule |
|---|---|
| `id` | Integer. Assigned when the worker is released. |
| `task_id` | The task. Required. |
| `worker_id` | The worker. Required. Unique. |
| `scale_id` | The scale that released the worker. Required. |
| `recorded_at` | The workspace time of the release. Required. |

An active worker is a worker with no release row. Released workers are not counted, do not receive jobs, and cannot steal.

## Task detail

The task detail includes, on `work`:

- `queue`: waiting names, oldest first.
- `plans`: each plan from oldest to newest, with `name`, `waiting`, `held`, `active`, and `needed`.
- `scales`: each scale from oldest to newest, with `name`, `direction`, `worker`, and `job`. `job` is null for a release.
- `released`: released worker names, oldest release first.
- `needed`: the workers needed now.
- `active`: the active workers now.
- `can_queue` and `can_plan`: true while the task is In Progress.
- `can_scale`: true while the task is In Progress and a scale would assign, add, or release.

`workers` stays the active workers only.

## State

- A queued name starts waiting.
- A fill or a scale-up creates the job, sets `job_id`, and stores the scale together.
- A release stores the scale and the release together. The worker row remains.
- A rolled-back scale leaves no scale, no new job, no new worker, and no release.
