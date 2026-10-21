# Data Model: Asynchronous Hyperband, ASHA, and Distributed Agent Scheduling

## asha_trial

| Column | Rule |
|---|---|
| id | Integer, increases by 1 |
| task_id | The task that owns the trial |
| name | Trimmed text, unique with the task |
| recorded_at | The time the trial was stored |

A task holds at most 4 rows. Rows are read oldest id first. The same name does not add a row. A new row removes the schedule.

## asha_runner

| Column | Rule |
|---|---|
| id | Integer, increases by 1 |
| task_id | The task that owns the runner |
| name | Trimmed text, unique with the task |
| recorded_at | The time the runner was stored |

A task holds at most 2 rows. Rows are read oldest id first. The same name does not add a row. A new row removes the schedule.

## asha_rung

| Column | Rule |
|---|---|
| id | Integer, increases by 1 |
| task_id | The task that owns the rung score |
| name | Trimmed text, unique with the task |
| trial_id | The trial on this task |
| rung | 1 or 2 |
| score | 1 or 2 |
| recorded_at | The time the score was stored |

A task holds at most 6 rows. A trial has at most one row at each rung, so `task_id`, `trial_id`, and `rung` are unique together. The same name does not add a row and does not change the other fields. A new rung 1 row removes the schedule. A new rung 2 row removes the winner and leaves the assignments.

## asha_promoted

| Column | Rule |
|---|---|
| id | Integer, increases by 1 |
| task_id | The task that owns the promoted row |
| trial | Trimmed trial name |
| position | 1 or greater, in promotion order |
| recorded_at | The time the schedule was stored |

The rows are the better half of the rung 1 scores recorded so far. They are read by position. Opening the task does not count them again.

## asha_assignment

| Column | Rule |
|---|---|
| id | Integer, increases by 1 |
| task_id | The task that owns the assignment |
| trial | Trimmed trial name, unique with the task |
| runner | Trimmed runner name |
| position | 1 or greater, in the order the assignments were stored |
| recorded_at | The time the assignment was stored |

A repeated schedule does not add a second row for the same trial.

## asha_winner

| Column | Rule |
|---|---|
| id | Integer, increases by 1 |
| task_id | One winner for the task |
| winner | Trimmed trial name |
| recorded_at | The time the winner was stored |

One row replaces the previous winner. It is stored only when every promoted trial has a rung 2 score.
