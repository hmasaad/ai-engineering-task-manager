# Commands: Distributed Bayesian Optimization and Decentralized Scheduling

## Name a point

`POST /api/tasks/{id}/consensus-points`

`POST /tasks/{id}/consensus-points`

Body: `name`, `setting`

The same name returns the task detail before the setting is checked.

## Name a node

`POST /api/tasks/{id}/consensus-nodes`

`POST /tasks/{id}/consensus-nodes`

Body: `name`

The same name returns the task detail before anything else is checked.

## Record a report

`POST /api/tasks/{id}/consensus-reports`

`POST /tasks/{id}/consensus-reports`

Body: `name`, `node`, `point`, `score`

The same name returns the task detail before the other fields are checked. The report count is checked before the same node and point are checked, so a fifth report reports the count.

## Agree on the next point

`POST /api/tasks/{id}/consensus-agreements`

`POST /tasks/{id}/consensus-agreements`

The body is empty.

## Task detail

The task detail gains `consensus`:

```json
{
  "points": [{"name": "ada", "setting": 1}],
  "nodes": [{"name": "north"}],
  "reports": [{"name": "one", "node": "north", "point": "ada", "score": 2}],
  "proposals": [{"node": "north", "point": "mina"}],
  "choice": null,
  "can_name": true,
  "can_node": true,
  "can_report": true,
  "can_agree": true
}
```

`proposals` is an empty list, and `choice` is null, when no agreement is stored. A stored choice is `{"point": "mina", "node": "north", "suggestions": 2}`. `setting`, `score`, and `suggestions` are integers. Points, nodes, reports, and proposals are oldest first. The payload does not use the keys `values`, `items`, or `keys`.

## Page

The Consensus section is after Hyperband and before Executions.

- Points: `ada: 1`
- Nodes: `north`
- Reports: `one: north, ada, score 2`
- Suggestions: `north: mina`
- Agreement: `Agreement: mina on north, 2 suggestions`
- Empty points: `No points yet.`
- Name point uses `id="consensus-point-name"` and `id="consensus-point-setting"` while the task is In Progress.
- Name node uses `id="consensus-node-name"` while the task is In Progress.
- Record report uses `id="consensus-report-name"`, `id="consensus-report-node"`, `id="consensus-report-point"`, and `id="consensus-report-score"` only while a point and a node exist.
- Agree on a design is offered only while a report exists.
- The button texts are `Name point`, `Name node`, `Record report`, and `Agree on a design`.

## Refusals

| Condition | Response |
|---|---|
| Blank point name | 400 `Name this point.` |
| Setting other than 1 or 2 | 400 `Name a setting of 1 or 2.` |
| Fifth point | 409 `This task already has 4 points.` |
| Blank node name | 400 `Name this node.` |
| Third node | 409 `This task already has 2 nodes.` |
| Blank report name | 400 `Name this report.` |
| Blank report node | 400 `Name the node.` |
| Blank report point | 400 `Name the point.` |
| Score other than 1 or 2 | 400 `Name a score of 1 or 2.` |
| Report node is not on this task | 409 `That node is not on this task.` |
| Report point is not on this task | 409 `That point is not on this task.` |
| Node already reported this point | 409 `That node already reported this point.` |
| Fifth report | 409 `This task already has 4 reports.` |
| Agreement with no point | 409 `Name a point first.` |
| Agreement with no node | 409 `Name a node first.` |
| Agreement with no report | 409 `Record a report first.` |
| Every node has reported every point | 409 `No point is left to try.` |
| Task is not In Progress | 409 `The task must be In Progress.` |
| Task is missing | 404 `Task not found.` |
| Repeated point, node, or report name | 200 task detail |
