# Data Model: Multi-Armed Bandits, Thompson Sampling, and Contextual Exploration

## explore_arm

| Column | Rule |
|---|---|
| id | Integer, increases by 1 |
| task_id | The task that owns the arm |
| name | Trimmed text, unique with the task |
| recorded_at | The time the arm was stored |

A task holds at most 2 rows. Rows are read oldest id first. The same name does not add a row. A new row removes the draw.

## explore_context

| Column | Rule |
|---|---|
| id | Integer, increases by 1 |
| task_id | The task that owns the context |
| name | Trimmed text, unique with the task |
| recorded_at | The time the context was stored |

A task holds at most 2 rows. Rows are read oldest id first. The same name does not add a row. A new row removes the draw.

## explore_pull

| Column | Rule |
|---|---|
| id | Integer, increases by 1 |
| task_id | The task that owns the pull |
| name | Trimmed text, unique with the task |
| context_id | The context on this task |
| arm_id | The arm on this task |
| reward | 1 or 2 |
| recorded_at | The time the pull was stored |

A task holds at most 4 rows. The context and the arm must already be stored. A reward of 2 is a win. A reward of 1 is a loss. The same name does not add a row and does not change the other fields. A new row removes the draw.

## explore_draw

| Column | Rule |
|---|---|
| id | Integer, increases by 1 |
| task_id | One draw for the task |
| context | Trimmed context name |
| arm | Trimmed arm name that was chosen |
| sample | `middle`, `high`, or `low` |
| step | 1 for the first draw after a reset, then 2, then 3, and so on |
| recorded_at | The time the draw was stored |

One row replaces the previous draw. Step 1, 4, 7, and so on use the middle score. Step 2, 5, 8, and so on use the high score. Step 3, 6, 9, and so on use the low score. Deleting the row restarts the next draw at step 1. The scores are counted from the pulls when the draw is stored. Opening the task does not count them again.
