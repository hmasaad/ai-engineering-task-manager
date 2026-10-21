# Commands: Multi-Fidelity Bayesian Optimization and Successive Halving

## Name a candidate

`POST /api/tasks/{id}/fidelity-candidates`

`POST /tasks/{id}/fidelity-candidates`

Body: `name`

The same name returns the task detail before anything else is checked.

## Record a measurement

`POST /api/tasks/{id}/fidelity-measurements`

`POST /tasks/{id}/fidelity-measurements`

Body: `name`, `candidate`, `fidelity`, `score`

The same name returns the task detail before the other fields are checked. The measurement count is checked before the same candidate and fidelity are checked, so a seventh measurement reports the count.

## Halve the field

`POST /api/tasks/{id}/fidelity-halves`

`POST /tasks/{id}/fidelity-halves`

The body is empty.

## Task detail

The task detail gains `fidelity`:

```json
{
  "candidates": [{"name": "ada"}],
  "measurements": [
    {"name": "one", "candidate": "ada", "fidelity": 1, "score": 1}
  ],
  "kept": [{"name": "grace"}, {"name": "mina"}],
  "winner": "mina",
  "can_name": true,
  "can_measure": true,
  "can_halve": true
}
```

`kept` is an empty list and `winner` is null when no halving is stored. `fidelity` and `score` are integers. Candidates, measurements, and kept names are oldest first. The payload does not use the keys `values`, `items`, or `keys`.

## Page

The Fidelity section is after Search and before Executions.

- Candidates: `ada`
- Measurements: `one: ada, fidelity 1, score 2`
- Kept names: `grace`
- Winner: `Winner: mina`
- Empty candidates: `No candidates yet.`
- Name candidate uses `id="fidelity-candidate-name"` while the task is In Progress.
- Record fidelity uses `id="fidelity-measurement-name"`, `id="fidelity-measurement-candidate"`, `id="fidelity-level"`, and `id="fidelity-score"` only while a candidate exists.
- Halve the field is offered only while two cheap measurements exist.
- The button texts are `Name candidate`, `Record fidelity`, and `Halve the field`.

## Refusals

| Condition | Response |
|---|---|
| Blank candidate name | 400 `Name this candidate.` |
| Fifth candidate | 409 `This task already has 4 candidates.` |
| Blank measurement name | 400 `Name this measurement.` |
| Blank measurement candidate | 400 `Name the candidate.` |
| Fidelity other than 1 or 2 | 400 `Name a fidelity of 1 or 2.` |
| Score other than 1 or 2 | 400 `Name a score of 1 or 2.` |
| Measurement candidate is not on this task | 409 `That candidate is not on this task.` |
| Candidate already has this fidelity | 409 `That candidate already has this fidelity.` |
| Seventh measurement | 409 `This task already has 6 measurements.` |
| Fidelity 2 before a halving | 409 `Halve the field before an expensive measurement.` |
| Fidelity 2 for a candidate who was not kept | 409 `That candidate was not kept.` |
| Halving with no candidate | 409 `Name a candidate first.` |
| Halving with one candidate | 409 `Name another candidate first.` |
| A candidate has no cheap measurement | 409 `Record a cheap measurement for every candidate first.` |
| Task is not In Progress | 409 `The task must be In Progress.` |
| Task is missing | 404 `Task not found.` |
| Repeated candidate or measurement name | 200 task detail |
