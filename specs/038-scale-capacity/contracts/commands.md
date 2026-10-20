# Commands: Autoscaling and Queue-Based Capacity Planning

## Queue work

`POST /api/tasks/{task_id}/queue`

`POST /tasks/{task_id}/queue`

```json
{ "name": "one" }
```

`name` may be omitted. The page field is Waiting work, `id="queue-name"`. The button is Queue work.

The trimmed name is stored once and waits. The same name returns the task detail and does not queue another item.

## Plan capacity

`POST /api/tasks/{task_id}/plans`

`POST /tasks/{task_id}/plans`

```json
{ "name": "now" }
```

`name` may be omitted. The page field is Plan name, `id="plan-name"`. The button is Plan capacity.

The trimmed name is stored once with the waiting count, the held count, the active workers, and the workers needed. The same name returns the task detail and does not record another plan.

## Scale workers

`POST /api/tasks/{task_id}/scales`

`POST /tasks/{task_id}/scales`

```json
{ "name": "grace" }
```

`name` may be omitted. The page field is Scale name, `id="scale-name"`. The button is Scale workers.

The trimmed name is stored once.

- `fill` assigns the oldest waiting item to the least-loaded active worker. Equal counts choose the worker stored first.
- `up` adds a worker with that name and assigns the oldest waiting item to that worker.
- `down` releases the newest active worker who holds nothing.

Spare room is used before a worker is added. A release is used only when the active workers are more than the workers needed and no waiting item can be assigned.

## Task detail

The task detail includes, on `work`:

```json
{
  "queue": ["four"],
  "plans": [
    { "name": "now", "waiting": 4, "held": 0, "active": 0, "needed": 2 }
  ],
  "scales": [
    { "name": "grace", "direction": "up", "worker": "grace", "job": "one" }
  ],
  "released": ["lin"],
  "needed": 2,
  "active": 1,
  "can_queue": true,
  "can_plan": true,
  "can_scale": true
}
```

`queue`, `plans`, `scales`, and `released` are oldest first.

## Refusals

| Condition | Status | Message |
|---|---|---|
| Blank waiting name | 400 | `Name this work.` |
| Blank plan name | 400 | `Name this plan.` |
| Blank scale name | 400 | `Name this scale.` |
| The name is already a held job | 409 | `That work is already on this task.` |
| The scale would add a worker whose name is taken | 409 | `That worker is already on this task.` |
| Every extra worker holds a job | 409 | `Every extra worker holds a job.` |
| The queue already matches and nothing can be assigned | 409 | `The queue already has the workers it needs.` |
| The task is not In Progress | 409 | `The task must be In Progress.` |
| Unknown task | 404 | `Task not found.` |

A refusal does not store the name. `GET /api/tasks` stays the list of tasks. A direct placement onto a full active worker is still `Every worker is full.`

## Page

The task page shows `Workers needed: 2. Active workers: 1.` Waiting names are listed under Waiting work. A plan is `now — waiting 4, held 0, needed 2, active 0`. A scale is `grace scaled up with one`, `fill assigned one to ada`, or `trim released grace`. Queue work and Plan capacity are offered while the task is In Progress. Scale workers is offered while `can_scale` is true.
