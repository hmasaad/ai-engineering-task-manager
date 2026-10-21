# Commands: Asynchronous Hyperband, ASHA, and Distributed Agent Scheduling

## Name a trial

`POST /api/tasks/{id}/hyperband-trials`

`POST /tasks/{id}/hyperband-trials`

Body: `name`

The same name returns the task detail before anything else is checked.

## Name a runner

`POST /api/tasks/{id}/hyperband-runners`

`POST /tasks/{id}/hyperband-runners`

Body: `name`

The same name returns the task detail before anything else is checked.

## Record a rung score

`POST /api/tasks/{id}/hyperband-rungs`

`POST /tasks/{id}/hyperband-rungs`

Body: `name`, `trial`, `rung`, `score`

The same name returns the task detail before the other fields are checked. The rung-score count is checked before the same trial and rung are checked, so a seventh score reports the count.

## Schedule the next trial

`POST /api/tasks/{id}/hyperband-schedules`

`POST /tasks/{id}/hyperband-schedules`

The body is empty.

## Task detail

The task detail gains `hyperband`:

```json
{
  "trials": [{"name": "red"}],
  "runners": [{"name": "ada"}],
  "rungs": [{"name": "one", "trial": "red", "rung": 1, "score": 1}],
  "promoted": [{"name": "blue"}],
  "assignments": [{"trial": "blue", "runner": "ada"}],
  "winner": null,
  "can_name": true,
  "can_runner": true,
  "can_record": true,
  "can_schedule": true
}
```

`promoted` and `assignments` are empty lists, and `winner` is null, when no schedule is stored. `rung` and `score` are integers. Trials, runners, rung scores, promoted names, and assignments are oldest first. The payload does not use the keys `values`, `items`, or `keys`.

## Page

The Hyperband section is after Allocation and before Executions.

- Trials: `red`
- Runners: `ada`
- Rung scores: `one: red, rung 1, score 1`
- Promoted trials: `blue`
- Assignments: `blue: ada`
- Winner: `Winner: gold`
- Empty trials: `No trials yet.`
- Name trial uses `id="hyperband-trial-name"` while the task is In Progress.
- Name runner uses `id="hyperband-runner-name"` while the task is In Progress.
- Record rung uses `id="hyperband-rung-name"`, `id="hyperband-rung-trial"`, `id="hyperband-rung-level"`, and `id="hyperband-rung-score"` only while a trial exists.
- Schedule the next trial is offered only while two rung 1 scores and a runner exist.
- The button texts are `Name trial`, `Name runner`, `Record rung`, and `Schedule the next trial`.

## Refusals

| Condition | Response |
|---|---|
| Blank trial name | 400 `Name this trial.` |
| Fifth trial | 409 `This task already has 4 trials.` |
| Blank runner name | 400 `Name this runner.` |
| Third runner | 409 `This task already has 2 runners.` |
| Blank rung-score name | 400 `Name this rung score.` |
| Blank rung trial | 400 `Name the trial.` |
| Rung other than 1 or 2 | 400 `Name a rung of 1 or 2.` |
| Score other than 1 or 2 | 400 `Name a score of 1 or 2.` |
| Rung trial is not on this task | 409 `That trial is not on this task.` |
| Trial already has this rung | 409 `That trial already has this rung.` |
| Seventh rung score | 409 `This task already has 6 rung scores.` |
| Rung 2 before two rung 1 scores | 409 `Record two rung scores first.` |
| Rung 2 for a trial that is not promoted | 409 `That trial is not promoted.` |
| Schedule with no trial | 409 `Name a trial first.` |
| Schedule with no runner | 409 `Name a runner first.` |
| Schedule before two rung 1 scores | 409 `Record two rung scores first.` |
| Task is not In Progress | 409 `The task must be In Progress.` |
| Task is missing | 404 `Task not found.` |
| Repeated trial, runner, or rung-score name | 200 task detail |
