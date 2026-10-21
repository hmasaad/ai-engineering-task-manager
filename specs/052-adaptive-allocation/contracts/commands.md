# Commands: Adaptive Resource Allocation for Workflow and Agent Optimization

## Name an agent

`POST /api/tasks/{id}/allocation-agents`

`POST /tasks/{id}/allocation-agents`

Body: `name`

The same name returns the task detail before anything else is checked.

## Record a yield

`POST /api/tasks/{id}/allocation-yields`

`POST /tasks/{id}/allocation-yields`

Body: `name`, `agent`, `value`

The same name returns the task detail before the other fields are checked. The yield count is checked before the same agent is checked, so a fifth yield reports the count.

## Allocate the pool

`POST /api/tasks/{id}/allocation-shares`

`POST /tasks/{id}/allocation-shares`

The body is empty.

## Task detail

The task detail gains `allocation`:

```json
{
  "agents": [{"name": "ada"}],
  "yields": [{"name": "one", "agent": "ada", "value": 2}],
  "shares": [{"agent": "ada", "units": 3}, {"agent": "grace", "units": 1}],
  "can_name": true,
  "can_record": true,
  "can_allocate": true
}
```

`shares` is an empty list when no allocation is stored. `value` and `units` are integers. Agents, yields, and shares are oldest first. The payload does not use the keys `values`, `items`, or `keys`.

## Page

The Allocation section is after Fidelity and before Executions.

- Agents: `ada`
- Yields: `one: ada, yield 2`
- Shares: `ada: 3`
- Empty agents: `No agents yet.`
- Name agent uses `id="allocation-agent-name"` while the task is In Progress.
- Record yield uses `id="allocation-yield-name"`, `id="allocation-yield-agent"`, and `id="allocation-yield-value"` only while an agent exists.
- Allocate the pool is offered only while a yield exists.
- The button texts are `Name agent`, `Record yield`, and `Allocate the pool`.
- A share of 0 is shown.

## Refusals

| Condition | Response |
|---|---|
| Blank agent name | 400 `Name this agent.` |
| Fifth agent | 409 `This task already has 4 agents.` |
| Blank yield name | 400 `Name this yield.` |
| Blank yield agent | 400 `Name the agent.` |
| Value other than 1 or 2 | 400 `Name a yield of 1 or 2.` |
| Yield agent is not on this task | 409 `That agent is not on this task.` |
| Agent already has a yield | 409 `That agent already has a yield.` |
| Fifth yield | 409 `This task already has 4 yields.` |
| Allocation with no agent | 409 `Name an agent first.` |
| An agent has no yield | 409 `Record a yield for every agent first.` |
| Task is not In Progress | 409 `The task must be In Progress.` |
| Task is missing | 404 `Task not found.` |
| Repeated agent or yield name | 200 task detail |
