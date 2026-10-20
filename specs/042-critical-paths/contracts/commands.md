# Commands: Workflow Scheduling with Dependencies, Critical Paths, and Deadline Propagation

## Name step

`POST /api/tasks/{task_id}/schedule-steps`

`POST /tasks/{task_id}/schedule-steps`

```json
{ "name": "design", "length": "1" }
```

`name` and `length` may be omitted. The page fields are Step name, `id="schedule-step-name"`, and Length, `id="step-length"`. The button is Name step.

The trimmed name is stored once at the given length. The length is accepted only when the trimmed text is `1` or `2`. The same name returns the task detail and does not change the length.

## Add dependency

`POST /api/tasks/{task_id}/schedule-links`

`POST /tasks/{task_id}/schedule-links`

```json
{ "step": "build", "follows": "design" }
```

`step` and `follows` may be omitted. The page fields are Step, `id="link-step"`, and Follows, `id="link-follows"`. The button is Add dependency.

The trimmed step follows the trimmed earlier step. The same link returns the task detail and does not store another link.

## Set deadline

`POST /api/tasks/{task_id}/schedule-deadlines`

`POST /tasks/{task_id}/schedule-deadlines`

```json
{ "deadline": "2026-12-03T00:00:00Z" }
```

`deadline` may be omitted. The page field is Deadline, `id="path-deadline"`. The button is Set deadline.

The trimmed deadline is stored once for the task. The same deadline returns the task detail. A different deadline replaces the stored deadline.

## Task detail

The task detail includes `paths`:

```json
{
  "steps": [
    { "name": "design", "length": 1, "follows": null, "latest": "2026-12-01T00:00:00Z" },
    { "name": "build", "length": 2, "follows": "design", "latest": "2026-12-03T00:00:00Z" }
  ],
  "critical": ["design", "build"],
  "deadline": "2026-12-03T00:00:00Z",
  "can_name": true,
  "can_link": true,
  "can_deadline": true
}
```

`steps` are oldest first. `follows` is null when the step follows nothing. `latest` is null when no deadline is stored. `critical` is the critical path from the first step to the last. `can_name` is true while the task is In Progress. `can_link` is true while the task is In Progress and at least two steps exist. `can_deadline` is true while the task is In Progress and at least one step exists.

## Page

The task page shows a Workflow schedule section.

- Each step is `design: length 1` or `build: length 2, follows design` in `id="schedule-steps"`. With a deadline, the line adds `, latest 2026-12-01T00:00:00Z`.
- The critical path is `Critical path: design, build` in `id="critical-path"`.
- The deadline is `Deadline: 2026-12-03T00:00:00Z` in `id="schedule-deadline"`.
- Name step is offered while the task is In Progress.
- Add dependency is offered only while `can_link` is true.
- Set deadline is offered only while `can_deadline` is true.

## Refusals

| Condition | Status | Message |
|---|---|---|
| Blank step name | 400 | `Name this step.` |
| Length is not 1 or 2 | 400 | `Name a length of 1 or 2.` |
| Blank follower | 400 | `Name the step that follows.` |
| Blank predecessor | 400 | `Name the step it follows.` |
| Step is not on this task | 409 | `That step is not on this task.` |
| A step follows itself | 409 | `A step cannot follow itself.` |
| The step already follows a different step | 409 | `That step already follows another step.` |
| The link would form a cycle | 409 | `Those steps would form a cycle.` |
| Deadline is not a real UTC time in the required form | 400 | `Name a deadline.` |
| No step has been named | 409 | `Name a step first.` |
| Task is not In Progress | 409 | `The task must be In Progress.` |
| Task is missing | 404 | `Task not found.` |

A repeated step name, a repeated link, or the same deadline returns the task detail with status 200.
