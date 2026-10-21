# Data Model: Constrained and Multi-Objective Bayesian Optimization

## bayes_design

| Column | Rule |
|---|---|
| id | Integer, increases by 1 |
| task_id | The task that owns the design |
| name | Trimmed text, unique with the task |
| first_setting | 1 or 2 |
| second_setting | 1 or 2 |
| recorded_at | The time the design was stored |

A task holds at most 4 rows. Rows are read oldest id first. The same name does not add a row and does not change the settings. A new row removes the recommendation.

## bayes_observation

| Column | Rule |
|---|---|
| id | Integer, increases by 1 |
| task_id | The task that owns the observation |
| name | Trimmed text, unique with the task |
| design_id | The design on this task, unique with the task |
| first_objective | 1 or 2 |
| second_objective | 1 or 2 |
| constraint_mark | 1 or 2 |
| recorded_at | The time the observation was stored |

A task holds at most 4 rows. A design has at most one row. A constraint of 1 is feasible. A constraint of 2 is violated. The same name does not add a row and does not change the other fields. A new row removes the recommendation.

## bayes_pick

| Column | Rule |
|---|---|
| id | Integer, increases by 1 |
| task_id | One recommendation for the task |
| next_design | Trimmed design name |
| recorded_at | The time the recommendation was stored |

One row replaces the previous recommendation. Deleting the row also deletes the front rows.

## bayes_front

| Column | Rule |
|---|---|
| id | Integer, increases by 1 |
| task_id | The task that owns the front row |
| design | Trimmed design name |
| first_objective | 1 or 2 |
| second_objective | 1 or 2 |
| position | 1 or greater, in observation order |
| recorded_at | The time the recommendation was stored |

The rows are the feasible observations that are not dominated. They are read by position. Opening the task does not count them again.
