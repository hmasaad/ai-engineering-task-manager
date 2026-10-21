# Data Model: Multi-Fidelity Bayesian Optimization and Successive Halving

## fidelity_candidate

| Column | Rule |
|---|---|
| id | Integer, increases by 1 |
| task_id | The task that owns the candidate |
| name | Trimmed text, unique with the task |
| recorded_at | The time the candidate was stored |

A task holds at most 4 rows. Rows are read oldest id first. The same name does not add a row. A new row removes the kept names and the winner.

## fidelity_measurement

| Column | Rule |
|---|---|
| id | Integer, increases by 1 |
| task_id | The task that owns the measurement |
| name | Trimmed text, unique with the task |
| candidate_id | The candidate on this task |
| fidelity | 1 or 2 |
| score | 1 or 2 |
| recorded_at | The time the measurement was stored |

A task holds at most 6 rows. A candidate has at most one row at each fidelity, so `task_id`, `candidate_id`, and `fidelity` are unique together. Fidelity 1 is cheap. Fidelity 2 is expensive. The same name does not add a row and does not change the other fields. A new cheap row removes the kept names and the winner. A new expensive row removes the winner and leaves the kept names.

## fidelity_round

| Column | Rule |
|---|---|
| id | Integer, increases by 1 |
| task_id | One halving for the task |
| winner | Trimmed candidate name, or empty when no winner is stored |
| recorded_at | The time the halving was stored |

One row replaces the previous halving. Deleting the row also deletes the kept rows. Clearing the winner leaves the kept rows and stores an empty winner.

## fidelity_kept

| Column | Rule |
|---|---|
| id | Integer, increases by 1 |
| task_id | The task that owns the kept row |
| candidate | Trimmed candidate name |
| position | 1 or greater, in the order the half was chosen |
| recorded_at | The time the halving was stored |

The rows are the better half of the cheap scores. They are read by position. Opening the task does not count them again.
