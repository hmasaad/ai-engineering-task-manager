# Commands: Priority Scheduling, Aging, and Starvation Prevention

## Rank work

`POST /api/tasks/{task_id}/priorities`

`POST /tasks/{task_id}/priorities`

```json
{ "name": "quiet", "rank": "1" }
```

`name` and `rank` may be omitted. The page fields are Work name, `id="priority-name"`, and Rank, `id="work-rank"`. The button is Rank work.

The trimmed name is stored once at the given rank and at age 0. The rank is accepted only when the trimmed text is `1`, `2`, or `3`. The same name returns the task detail and does not change the rank or the age.

## Serve next

`POST /api/tasks/{task_id}/serves`

`POST /tasks/{task_id}/serves`

```json
{ "name": "one" }
```

`name` may be omitted. The page field is Serve name, `id="serve-name"`. The button is Serve next.

The trimmed name is stored once. The serve goes to the waiting work with the highest score. The score is rank plus age. Equal scores choose the work stored first. Every other piece of work that is still waiting ages by 1. The same name returns the task detail and does not age any work.

## Task detail

The task detail includes `priority`:

```json
{
  "waiting": [
    { "name": "quiet", "rank": 1, "age": 2 }
  ],
  "serves": [
    { "name": "one", "work": "rush" }
  ],
  "can_rank": true,
  "can_serve": true
}
```

`waiting` and `serves` are oldest first. `can_rank` is true while the task is In Progress. `can_serve` is true while the task is In Progress and at least one piece of work is waiting.

## Page

The task page shows a Priority section.

- Each waiting piece is `quiet: rank 1, age 2` in `id="priority-work"`.
- Each serve is `one served rush` in `id="priority-serves"`.
- Rank work is offered while the task is In Progress.
- Serve next is offered only while `can_serve` is true.

## Refusals

| Condition | Status | Message |
|---|---|---|
| Blank work name | 400 | `Name this work.` |
| Rank is not 1, 2, or 3 | 400 | `Name a rank from 1 to 3.` |
| Blank serve name | 400 | `Name this serve.` |
| No work is waiting | 409 | `Rank work before serving.` |
| Task is not In Progress | 409 | `The task must be In Progress.` |
| Task is missing | 404 | `Task not found.` |

A repeated work name or serve name returns the task detail with status 200.
