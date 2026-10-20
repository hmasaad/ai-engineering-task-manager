# Commands: Work Stealing, Backpressure, and Load Balancing

## Add a worker

`POST /api/tasks/{task_id}/workers`

`POST /tasks/{task_id}/workers`

```json
{ "name": "ada" }
```

`name` may be omitted. The page field is Worker name, `id="worker-name"`. The button is Add worker.

The trimmed name is stored once. The same name returns the task detail and does not add a worker.

## Place a job

`POST /api/tasks/{task_id}/jobs`

`POST /tasks/{task_id}/jobs`

```json
{ "name": "one" }
```

`name` may be omitted. The page field is Job name, `id="job-name"`. The button is Place job.

The trimmed name is stored once, on the worker with the fewest pending jobs. Equal counts choose the worker stored first. The same name returns the task detail and does not place another job.

## Steal work

`POST /api/tasks/{task_id}/steals`

`POST /tasks/{task_id}/steals`

```json
{ "name": "take", "worker": "lin" }
```

`name` and `worker` may be omitted. The page fields are Steal name, `id="steal-name"`, and Idle worker, `id="idle-worker"`. The button is Steal work.

The trimmed steal name is stored once. `worker` is the idle worker who takes the oldest job from the other worker with the most pending jobs. Equal counts choose the worker stored first. The same steal name returns the task detail and does not move another job.

## Task detail

The task detail includes:

```json
{
  "work": {
    "workers": [
      { "name": "ada", "jobs": ["three"] },
      { "name": "lin", "jobs": ["one"] }
    ],
    "steals": [
      { "name": "take", "job": "one", "from_worker": "ada", "to_worker": "lin" }
    ],
    "can_place": true,
    "can_steal": false
  }
}
```

`workers` and `steals` are oldest first. `jobs` is oldest first.

## Refusals

| Condition | Status | Message |
|---|---|---|
| Blank worker name | 400 | `Name this worker.` |
| Blank job name | 400 | `Name this job.` |
| Blank steal name | 400 | `Name this steal.` |
| Blank idle worker | 400 | `Name the idle worker.` |
| No worker | 409 | `Name a worker first.` |
| The least-loaded worker holds three jobs | 409 | `Every worker is full.` |
| The named worker is absent | 409 | `That worker is not on this task.` |
| The named worker holds a job | 409 | `That worker is not idle.` |
| No other worker holds a job | 409 | `There is no work to steal.` |
| The task is not In Progress | 409 | `The task must be In Progress.` |
| Unknown task | 404 | `Task not found.` |

A refusal does not store the name. `GET /api/tasks` stays the list of tasks.

## Page

The task page lists each worker as `ada: one, three`, or `lin: idle` when that worker holds nothing. Each steal is `take moved one from ada to lin`. Add worker is offered while the task is In Progress. Place job is offered while `can_place` is true. Steal work is offered while `can_steal` is true.
