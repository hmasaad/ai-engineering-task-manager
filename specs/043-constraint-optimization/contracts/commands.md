# Commands: Constraint Programming and Optimization for Workflow Scheduling

## Name activity

`POST /api/tasks/{task_id}/opt-activities`

`POST /tasks/{task_id}/opt-activities`

```json
{ "name": "design", "length": "1" }
```

`name` and `length` may be omitted. The page fields are Activity name, `id="opt-activity-name"`, and Length, `id="activity-length"`. The button is Name activity.

The trimmed name is stored once at the given length. The length is accepted only when the trimmed text is `1` or `2`. The same name returns the task detail and does not change the length. A task stores at most 4 activities. A new activity removes the stored plan.

## Add constraint

`POST /api/tasks/{task_id}/opt-constraints`

`POST /tasks/{task_id}/opt-constraints`

```json
{ "activity": "test", "after": "build" }
```

`activity` and `after` may be omitted. The page fields are Activity, `id="constraint-activity"`, and After, `id="constraint-after"`. The button is Add constraint.

The trimmed activity cannot start until the trimmed earlier activity has finished. The same pair returns the task detail and does not store another constraint. A new constraint removes the stored plan.

## Set capacity

`POST /api/tasks/{task_id}/opt-capacities`

`POST /tasks/{task_id}/opt-capacities`

```json
{ "capacity": "2" }
```

`capacity` may be omitted. The page field is Capacity, `id="opt-capacity"`. The button is Set capacity.

The trimmed capacity is `1` or `2`. The same capacity returns the task detail and leaves the plan in place. A different capacity replaces the stored capacity and removes the plan.

## Optimize schedule

`POST /api/tasks/{task_id}/opt-plans`

`POST /tasks/{task_id}/opt-plans`

The body may be empty. The button is Optimize schedule.

The command stores one plan. Each activity has a start day. The finish day is the earliest day on which every legal schedule can be done. Equal finish days choose the schedule that starts the earliest-named activity sooner, then the next activity, and so on.

## Task detail

The task detail includes `optimization`:

```json
{
  "activities": [
    { "name": "design", "length": 1, "start": 0 },
    { "name": "build", "length": 2, "start": 0 },
    { "name": "test", "length": 1, "start": 2 }
  ],
  "constraints": [
    { "activity": "test", "after": "build" }
  ],
  "capacity": 2,
  "finish": 3,
  "can_name": true,
  "can_constrain": true,
  "can_bound": true,
  "can_optimize": true
}
```

`activities` and `constraints` are oldest first. `start` is null when no plan is stored. `capacity` and `finish` are null when they are not stored. `can_name` is true while the task is In Progress. `can_constrain` is true while the task is In Progress and at least two activities exist. `can_bound` is true while the task is In Progress and at least one activity exists. `can_optimize` is true while the task is In Progress, at least one activity exists, and a capacity is stored.

## Page

The task page shows an Optimization section.

- Each activity is `design: length 1` in `id="opt-activities"`. With a plan, the line adds `, starts 0`.
- Each constraint is `test after build` in `id="opt-constraints"`.
- The capacity is `Capacity: 2` in `id="opt-capacity-line"`.
- The finish day is `Finish day: 3` in `id="opt-finish"`.
- Name activity is offered while the task is In Progress.
- Add constraint is offered only while `can_constrain` is true.
- Set capacity is offered only while `can_bound` is true.
- Optimize schedule is offered only while `can_optimize` is true.

## Refusals

| Condition | Status | Message |
|---|---|---|
| Blank activity name | 400 | `Name this activity.` |
| Length is not 1 or 2 | 400 | `Name a length of 1 or 2.` |
| The task already has 4 activities | 409 | `This schedule already has 4 activities.` |
| Blank later activity | 400 | `Name the activity.` |
| Blank earlier activity | 400 | `Name the earlier activity.` |
| Activity is not on this task | 409 | `That activity is not on this task.` |
| An activity follows itself | 409 | `An activity cannot follow itself.` |
| The constraint would form a cycle | 409 | `Those activities would form a cycle.` |
| Capacity is not 1 or 2 | 400 | `Name a capacity of 1 or 2.` |
| No activity has been named | 409 | `Name an activity first.` |
| No capacity has been set | 409 | `Name a capacity first.` |
| Task is not In Progress | 409 | `The task must be In Progress.` |
| Task is missing | 404 | `Task not found.` |

A repeated activity name, a repeated constraint pair, or the same capacity returns the task detail with status 200.
