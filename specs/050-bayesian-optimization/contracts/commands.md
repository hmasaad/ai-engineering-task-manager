# Commands: Constrained and Multi-Objective Bayesian Optimization

## Name a design

`POST /api/tasks/{id}/search-designs`

`POST /tasks/{id}/search-designs`

Body: `name`, `first`, `second`

The same name returns the task detail before the settings are checked.

## Record an observation

`POST /api/tasks/{id}/search-observations`

`POST /tasks/{id}/search-observations`

Body: `name`, `design`, `first`, `second`, `constraint`

The same name returns the task detail before the other fields are checked.

## Recommend a design

`POST /api/tasks/{id}/search-recommendations`

`POST /tasks/{id}/search-recommendations`

The body is empty.

## Task detail

The task detail gains `search`:

```json
{
  "designs": [{"name": "ada", "first": 1, "second": 1}],
  "observations": [
    {"name": "one", "design": "ada", "first": 2, "second": 1, "constraint": 1}
  ],
  "front": [{"design": "ada", "first": 2, "second": 1}],
  "next": "mina",
  "can_name": true,
  "can_observe": true,
  "can_recommend": true
}
```

`front` is an empty list and `next` is null when no recommendation is stored. `first`, `second`, and `constraint` are integers. Designs and observations are oldest first.

## Page

The Search section is after Models and before Executions.

- Designs: `ada: 1, 1`
- Observations: `one: ada, objectives 2 and 1, constraint 1`
- Front: `ada: 2, 1`
- Next design: `Next design: mina`
- Empty designs: `No designs yet.`
- Name design uses `id="search-design-name"`, `id="search-first"`, and `id="search-second"` while the task is In Progress.
- Record observation uses `id="search-observation-name"`, `id="search-observation-design"`, `id="search-objective-first"`, `id="search-objective-second"`, and `id="search-constraint"` only while a design exists.
- Recommend a design is offered only while an observation exists.

## Refusals

| Condition | Response |
|---|---|
| Blank design name | 400 `Name this design.` |
| Setting other than 1 or 2 | 400 `Name a setting of 1 or 2.` |
| Fifth design | 409 `This task already has 4 designs.` |
| Blank observation name | 400 `Name this observation.` |
| Blank observation design | 400 `Name the design.` |
| Objective other than 1 or 2 | 400 `Name an objective of 1 or 2.` |
| Constraint other than 1 or 2 | 400 `Name a constraint of 1 or 2.` |
| Observation design is not on this task | 409 `That design is not on this task.` |
| Design already has an observation | 409 `That design already has an observation.` |
| Fifth observation | 409 `This task already has 4 observations.` |
| Recommendation with no design | 409 `Name a design first.` |
| Recommendation with no feasible observation | 409 `Record a feasible observation first.` |
| Every design has an observation | 409 `No design is left to try.` |
| Task is not In Progress | 409 `The task must be In Progress.` |
| Task is missing | 404 `Task not found.` |
| Repeated design or observation name | 200 task detail |
