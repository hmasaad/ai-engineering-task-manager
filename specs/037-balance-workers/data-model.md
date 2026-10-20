# Data Model: Work Stealing, Backpressure, and Load Balancing

## Worker

One named worker on one task.

| Field | Rule |
|---|---|
| `id` | Integer. Assigned when the worker is stored. The smaller id is the worker named first. |
| `task_id` | The task. Required. |
| `name` | Trimmed text. Required. Unique on the task. |
| `recorded_at` | The workspace time when the worker was stored. Required. |

A second insert for the same task and name does not add a row.

## Job

One named piece of pending work, held by one worker.

| Field | Rule |
|---|---|
| `id` | Integer. Assigned when the job is stored. The smaller id is the older job. |
| `task_id` | The task. Required. |
| `worker_id` | The worker who holds the job. Required. A steal changes this field. |
| `name` | Trimmed text. Required. Unique on the task. |
| `recorded_at` | The workspace time when the job was stored. Required. |

A job is not given a completed state. Pending means the job has a row.

## Steal

One accepted name for one move.

| Field | Rule |
|---|---|
| `id` | Integer. Assigned when the steal is stored. |
| `task_id` | The task. Required. |
| `job_id` | The job that moved. Required. |
| `from_worker_id` | The worker who held the job. Required. |
| `to_worker_id` | The idle worker who took the job. Required. |
| `name` | Trimmed text. Required. Unique on the task. |
| `recorded_at` | The workspace time when the steal was stored. Required. |

A second insert for the same task and name does not add a row. The job's worker and the steal row commit together.

## Task detail

The task detail includes `work`:

- `workers`: each worker from oldest to newest, with `name` and `jobs`. `jobs` lists the names that worker holds, oldest first. An empty list means the worker is idle.
- `steals`: each steal from oldest to newest, with `name`, `job`, `from_worker`, and `to_worker`.
- `can_place`: true only while the task is In Progress, at least one worker exists, and the least-loaded worker holds fewer than three jobs.
- `can_steal`: true only while the task is In Progress, one worker holds no jobs, and a different worker holds at least one job.

## State

- Before an accepted job name, no job row exists.
- An accepted job names the least-loaded worker. Equal counts choose the earliest worker.
- A refused placement stores no job.
- An accepted steal changes `worker_id` and stores the steal.
- A rolled-back steal leaves `worker_id` unchanged and leaves no steal row.

## Relationships

- A worker belongs to one task.
- A job belongs to one task and one worker.
- A steal belongs to one task, one job, and two workers on that task.
- The same names on another task are different rows.
