# Commands: Deadline-Aware Scheduling and Service-Level Objectives (SLOs)

## Set objective

`POST /api/tasks/{task_id}/objectives`

`POST /tasks/{task_id}/objectives`

```json
{ "name": "export", "deadline": "2026-12-01T00:00:00Z" }
```

`name` and `deadline` may be omitted. The page fields are Objective name, `id="objective-name"`, and Deadline, `id="objective-deadline"`. The button is Set objective.

The trimmed name is stored once with the given deadline. The deadline is accepted only when the trimmed text is a real UTC time in the form `2026-12-01T00:00:00Z`. The same name returns the task detail and does not change the deadline.

## Serve objective

`POST /api/tasks/{task_id}/objective-services`

`POST /tasks/{task_id}/objective-services`

```json
{ "name": "one" }
```

`name` may be omitted. The page field is Service name, `id="service-name"`. The button is Serve objective.

The trimmed name is stored once. The service goes to the waiting objective with the earliest deadline. Equal deadlines choose the objective stored first. The service is `met` when its recorded time is at or before the deadline, and `missed` when its recorded time is after the deadline. The same name returns the task detail and does not serve again.

## Task detail

The task detail includes `slo`:

```json
{
  "waiting": [
    { "name": "export", "deadline": "2026-12-01T00:00:00Z" }
  ],
  "services": [
    { "name": "one", "objective": "rush", "result": "missed" }
  ],
  "can_set": true,
  "can_serve": true
}
```

`waiting` and `services` are oldest first. `can_set` is true while the task is In Progress. `can_serve` is true while the task is In Progress and at least one objective is waiting.

## Page

The task page shows an Objectives section.

- Each waiting objective is `export: due 2026-12-01T00:00:00Z` in `id="objectives"`.
- Each service is `one missed rush` or `two met export` in `id="objective-services"`.
- Set objective is offered while the task is In Progress.
- Serve objective is offered only while `can_serve` is true.

## Refusals

| Condition | Status | Message |
|---|---|---|
| Blank objective name | 400 | `Name this objective.` |
| Deadline is not a real UTC time in the required form | 400 | `Name a deadline.` |
| Blank service name | 400 | `Name this service.` |
| No objective has been set | 409 | `Name an objective first.` |
| Every objective has been served | 409 | `Every objective has been served.` |
| Task is not In Progress | 409 | `The task must be In Progress.` |
| Task is missing | 404 | `Task not found.` |

A repeated objective name or service name returns the task detail with status 200.
