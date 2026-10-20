# Data Model: Constraint Programming and Optimization for Workflow Scheduling

No column is added to an existing table.

## opt_activity

| Field | Rule |
|---|---|
| id | Integer primary key |
| task_id | Required. References `task(id)` |
| name | Required. Trimmed text, length greater than 0. Unique with `task_id` |
| length | Required integer. One of 1 or 2 |
| recorded_at | Required timestamp |

A task holds at most 4 rows. Oldest first is `id` ascending. A length of 1 is one day. A length of 2 is two days.

## opt_constraint

| Field | Rule |
|---|---|
| id | Integer primary key |
| task_id | Required. References `task(id)` |
| activity_id | Required. References `opt_activity(id)`. The activity that starts later |
| after_id | Required. References `opt_activity(id)`. The activity that must finish first |
| recorded_at | Required timestamp |

The pair (`activity_id`, `after_id`) is unique. The two ids differ. A link that reaches its own activity by walking earlier activities is a cycle and is not stored.

## opt_capacity

| Field | Rule |
|---|---|
| id | Integer primary key |
| task_id | Required. Unique. References `task(id)` |
| capacity | Required integer. One of 1 or 2 |
| recorded_at | Required timestamp |

One task has one capacity. A new value replaces the stored capacity and removes the plan.

## opt_plan

| Field | Rule |
|---|---|
| id | Integer primary key |
| task_id | Required. Unique. References `task(id)` |
| finish | Required integer, 0 or greater. The earliest finish day |
| recorded_at | Required timestamp |

## opt_placement

| Field | Rule |
|---|---|
| id | Integer primary key |
| plan_id | Required. References `opt_plan(id)` |
| activity_id | Required. Unique with `plan_id`. References `opt_activity(id)` |
| start | Required integer, 0 or greater |

One optimization replaces the plan and its placements. Day 0 is the first day. An activity occupies the days from `start` up to, and not including, `start + length`. On every day, the number of activities that occupy that day is at most `capacity`. A later activity starts at or after the finish day of each activity it waits for.
