# Commands: Multi-Armed Bandits, Thompson Sampling, and Contextual Exploration

## Name an arm

`POST /api/tasks/{id}/thompson-arms`

`POST /tasks/{id}/thompson-arms`

Body: `name`

The same name returns the task detail and does not change the arm.

## Name a context

`POST /api/tasks/{id}/thompson-contexts`

`POST /tasks/{id}/thompson-contexts`

Body: `name`

The same name returns the task detail and does not change the context.

## Record a pull

`POST /api/tasks/{id}/thompson-pulls`

`POST /tasks/{id}/thompson-pulls`

Body: `name`, `context`, `arm`, `reward`

The same name returns the task detail before the other fields are checked.

## Draw an arm

`POST /api/tasks/{id}/thompson-draws`

`POST /tasks/{id}/thompson-draws`

Body: `context`

## Task detail

The task detail gains `exploration`:

```json
{
  "arms": [{"name": "ada"}],
  "contexts": [{"name": "rush"}],
  "pulls": [{"name": "one", "context": "rush", "arm": "ada", "reward": 2}],
  "draw": {"context": "rush", "arm": "grace", "sample": "high"},
  "can_name": true,
  "can_context": true,
  "can_pull": true,
  "can_draw": true
}
```

`draw` is null when no draw is stored. `reward` is an integer. Arms, contexts, and pulls are oldest first.

## Page

The Exploration section is after Safety and before Executions.

- Arms: `ada`
- Contexts: `rush`
- Pulls: `one: rush, ada, reward 2`
- Draw: `Draw in rush: grace, high sample`
- Empty arms: `No arms yet.`
- Name arm uses `id="thompson-arm-name"` while the task is In Progress.
- Name context uses `id="thompson-context-name"` while the task is In Progress.
- Record pull uses `id="pull-name"`, `id="pull-context"`, `id="pull-arm"`, and `id="pull-reward"` only while the task has an arm and a context.
- Draw arm uses `id="draw-context"` only while the task has an arm and a context.

## Refusals

| Condition | Response |
|---|---|
| Blank arm name | 400 `Name this arm.` |
| Third arm | 409 `This task already has 2 arms.` |
| Blank context name | 400 `Name this context.` |
| Third context | 409 `This task already has 2 contexts.` |
| Blank pull name | 400 `Name this pull.` |
| Blank pull context | 400 `Name the context.` |
| Blank pull arm | 400 `Name the arm.` |
| Reward other than 1 or 2 | 400 `Name a reward of 1 or 2.` |
| Pull context is not on this task | 409 `That context is not on this task.` |
| Pull arm is not on this task | 409 `That arm is not on this task.` |
| Fifth pull | 409 `This task already has 4 pulls.` |
| Draw with no arm | 409 `Name an arm first.` |
| Blank draw context | 400 `Name the context to draw.` |
| Draw with no context | 409 `Name a context first.` |
| Draw context is not on this task | 409 `That context is not on this task.` |
| Task is not In Progress | 409 `The task must be In Progress.` |
| Task is missing | 404 `Task not found.` |
| Repeated arm, context, or pull name | 200 task detail |
