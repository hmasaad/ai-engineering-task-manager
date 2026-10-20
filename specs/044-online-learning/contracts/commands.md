# Commands: Online Learning and Predictive Workflow Scheduling

## Record outcome

`POST /api/tasks/{task_id}/learn-outcomes`

`POST /tasks/{task_id}/learn-outcomes`

```json
{ "name": "past", "kind": "review", "length": "2" }
```

`name`, `kind`, and `length` may be omitted. The page fields are Outcome name, `id="outcome-name"`, Kind, `id="outcome-kind"`, and Length, `id="outcome-length"`. The button is Record outcome.

The trimmed name is stored once with the trimmed kind and the given length. The length is accepted only when the trimmed text is `1` or `2`. The same name returns the task detail and does not change the kind or the length. A task stores at most 4 outcomes. A new outcome removes the stored schedule.

## Name forecast

`POST /api/tasks/{task_id}/learn-forecasts`

`POST /tasks/{task_id}/learn-forecasts`

```json
{ "name": "draft", "kind": "review" }
```

`name` and `kind` may be omitted. The page fields are Forecast name, `id="forecast-name"`, and Kind, `id="forecast-kind"`. The button is Name forecast.

The trimmed forecast is upcoming work of the trimmed kind. The kind must already have an outcome on this task. The same name returns the task detail and does not change the kind. A task stores at most 4 forecasts. A new forecast removes the stored schedule.

## Predict schedule

`POST /api/tasks/{task_id}/learn-predictions`

`POST /tasks/{task_id}/learn-predictions`

The body may be empty. The button is Predict schedule.

The command stores one schedule. Each forecast receives the predicted length of its kind. Forecasts run one at a time, oldest first. The first starts on day 0. Each later forecast starts when the previous one is predicted to finish. The finish day is the end of the last forecast.

## Task detail

The task detail includes `learning`:

```json
{
  "outcomes": [
    { "name": "past", "kind": "review", "length": 2 },
    { "name": "again", "kind": "review", "length": 2 },
    { "name": "once", "kind": "export", "length": 1 }
  ],
  "kinds": [
    { "kind": "review", "predicted": 2 },
    { "kind": "export", "predicted": 1 }
  ],
  "forecasts": [
    { "name": "draft", "kind": "review", "predicted": 2, "start": 0 },
    { "name": "ship", "kind": "export", "predicted": 1, "start": 2 }
  ],
  "finish": 3,
  "can_record": true,
  "can_forecast": true,
  "can_predict": true
}
```

`outcomes`, `kinds`, and `forecasts` are oldest first. On a forecast, `predicted` and `start` are null when no schedule is stored. `finish` is null when no schedule is stored. `can_record` is true while the task is In Progress. `can_forecast` is true while the task is In Progress and at least one outcome exists. `can_predict` is true while the task is In Progress and at least one forecast exists.

## Page

The task page shows a Learning section.

- Each outcome is `past: review took 2` in `id="learn-outcomes"`.
- Each learned kind is `review: predicted 2` in `id="learned-kinds"`.
- Each forecast is `draft: review` in `id="learn-forecasts"`. With a schedule, the line adds `, predicted 2, starts 0`.
- The finish day is `Finish day: 3` in `id="learn-finish"`.
- Record outcome is offered while the task is In Progress.
- Name forecast is offered only while `can_forecast` is true.
- Predict schedule is offered only while `can_predict` is true.
- When no outcome exists, the section says `No outcomes yet.`

## Refusals

| Condition | Status | Message |
|---|---|---|
| Blank outcome name | 400 | `Name this outcome.` |
| Blank outcome kind | 400 | `Name this kind.` |
| Length is not 1 or 2 | 400 | `Name a length of 1 or 2.` |
| The task already has 4 outcomes | 409 | `This task already has 4 outcomes.` |
| Blank forecast name | 400 | `Name this forecast.` |
| Blank forecast kind | 400 | `Name the kind of work.` |
| The kind has no outcome | 409 | `Record an outcome for that kind first.` |
| The task already has 4 forecasts | 409 | `This task already has 4 forecasts.` |
| No forecast has been named | 409 | `Name a forecast first.` |
| Task is not In Progress | 409 | `The task must be In Progress.` |
| Task is missing | 404 | `Task not found.` |

A repeated outcome name or a repeated forecast name returns the task detail with status 200.
