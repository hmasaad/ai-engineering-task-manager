# Commands: Contextual Bandits with Linear Models and Neural Contextual Bandits

## Name an arm

`POST /api/tasks/{id}/model-arms`

`POST /tasks/{id}/model-arms`

Body: `name`

The same name returns the task detail and does not change the arm.

## Name a context

`POST /api/tasks/{id}/model-contexts`

`POST /tasks/{id}/model-contexts`

Body: `name`, `first`, `second`

The same name returns the task detail before the marks are checked.

## Record a pull

`POST /api/tasks/{id}/model-pulls`

`POST /tasks/{id}/model-pulls`

Body: `name`, `context`, `arm`, `reward`

The same name returns the task detail before the other fields are checked.

## Choose an arm

`POST /api/tasks/{id}/model-choices`

`POST /tasks/{id}/model-choices`

Body: `context`, `model`

## Task detail

The task detail gains `models`:

```json
{
  "arms": [{"name": "ada"}],
  "contexts": [{"name": "rush", "first": 1, "second": 1}],
  "pulls": [{"name": "one", "context": "quiet", "arm": "ada", "reward": 2}],
  "choice": {"context": "rush", "model": "neural", "arm": "grace"},
  "can_name": true,
  "can_context": true,
  "can_pull": true,
  "can_choose": true
}
```

`choice` is null when no choice is stored. `first`, `second`, and `reward` are integers. Arms, contexts, and pulls are oldest first.

## Page

The Models section is after Exploration and before Executions.

- Arms: `ada`
- Contexts: `rush: 1, 1`
- Pulls: `one: quiet, ada, reward 2`
- Linear choice: `Linear choice in rush: ada`
- Neural choice: `Neural choice in rush: grace`
- Empty arms: `No model arms yet.`
- Name model arm uses `id="model-arm-name"` while the task is In Progress.
- Name model context uses `id="model-context-name"`, `id="model-first"`, and `id="model-second"` while the task is In Progress.
- Record model pull uses `id="model-pull-name"`, `id="model-pull-context"`, `id="model-pull-arm"`, and `id="model-pull-reward"` only while the task has an arm and a context.
- Choose with model uses `id="model-choice-context"` and `id="model-choice-model"` only while the task has an arm and a context.

## Refusals

| Condition | Response |
|---|---|
| Blank arm name | 400 `Name this arm.` |
| Third arm | 409 `This task already has 2 arms.` |
| Blank context name | 400 `Name this context.` |
| Mark other than 0 or 1 | 400 `Name a mark of 0 or 1.` |
| Third context | 409 `This task already has 2 contexts.` |
| Blank pull name | 400 `Name this pull.` |
| Blank pull context | 400 `Name the context.` |
| Blank pull arm | 400 `Name the arm.` |
| Reward other than 1 or 2 | 400 `Name a reward of 1 or 2.` |
| Pull context is not on this task | 409 `That context is not on this task.` |
| Pull arm is not on this task | 409 `That arm is not on this task.` |
| Fifth pull | 409 `This task already has 4 pulls.` |
| Choice with no arm | 409 `Name an arm first.` |
| Blank choice context | 400 `Name the context to choose.` |
| Choice with no context | 409 `Name a context first.` |
| Choice context is not on this task | 409 `That context is not on this task.` |
| Blank model | 400 `Name the model.` |
| Model other than linear or neural | 400 `Name a linear or neural model.` |
| Task is not In Progress | 409 `The task must be In Progress.` |
| Task is missing | 404 `Task not found.` |
| Repeated arm, context, or pull name | 200 task detail |
