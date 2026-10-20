# Data Model: Online Learning and Predictive Workflow Scheduling

No column is added to an existing table.

## learn_outcome

| Field | Rule |
|---|---|
| id | Integer primary key |
| task_id | Required. References `task(id)` |
| name | Required. Trimmed text, length greater than 0. Unique with `task_id` |
| kind | Required. Trimmed text, length greater than 0 |
| length | Required integer. One of 1 or 2 |
| recorded_at | Required timestamp |

A task holds at most 4 rows. Oldest first is `id` ascending. A length of 1 is one day. A length of 2 is two days.

## Learned kind

A learned kind is not a separate table. It is each distinct `kind` among the outcomes of one task. Oldest kind first is the kind of the earliest outcome, then the next new kind. The predicted length is 2 when the number of outcomes of that kind with length 2 is greater than the number with length 1. Otherwise the predicted length is 1.

## learn_forecast

| Field | Rule |
|---|---|
| id | Integer primary key |
| task_id | Required. References `task(id)` |
| name | Required. Trimmed text, length greater than 0. Unique with `task_id` |
| kind | Required. Trimmed text. It must match the kind of an outcome on this task |
| recorded_at | Required timestamp |

A task holds at most 4 rows. Oldest first is `id` ascending.

## learn_plan

| Field | Rule |
|---|---|
| id | Integer primary key |
| task_id | Required. Unique. References `task(id)` |
| finish | Required integer, 0 or greater. The day the last forecast is predicted to finish |
| recorded_at | Required timestamp |

## learn_placement

| Field | Rule |
|---|---|
| id | Integer primary key |
| plan_id | Required. References `learn_plan(id)` |
| forecast_id | Required. Unique with `plan_id`. References `learn_forecast(id)` |
| predicted | Required integer. One of 1 or 2 |
| start | Required integer, 0 or greater |

One prediction replaces the plan and its placements. Forecasts run one at a time, oldest first. The first forecast starts on day 0. Each later forecast starts at the previous forecast's `start + predicted`. A forecast occupies the days from `start` up to, and not including, `start + predicted`. The finish day is the `start + predicted` of the last forecast.
