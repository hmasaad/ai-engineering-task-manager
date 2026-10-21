# Data Model: Contextual Bandits with Linear Models and Neural Contextual Bandits

## model_arm

| Column | Rule |
|---|---|
| id | Integer, increases by 1 |
| task_id | The task that owns the arm |
| name | Trimmed text, unique with the task |
| recorded_at | The time the arm was stored |

A task holds at most 2 rows. Rows are read oldest id first. The same name does not add a row. A new row removes the choice.

## model_context

| Column | Rule |
|---|---|
| id | Integer, increases by 1 |
| task_id | The task that owns the context |
| name | Trimmed text, unique with the task |
| first_mark | 0 or 1 |
| second_mark | 0 or 1 |
| recorded_at | The time the context was stored |

A task holds at most 2 rows. Rows are read oldest id first. The same name does not add a row and does not change the marks. A new row removes the choice.

## model_pull

| Column | Rule |
|---|---|
| id | Integer, increases by 1 |
| task_id | The task that owns the pull |
| name | Trimmed text, unique with the task |
| context_id | The context on this task |
| arm_id | The arm on this task |
| reward | 1 or 2 |
| recorded_at | The time the pull was stored |

A task holds at most 4 rows. The context and the arm must already be stored. The same name does not add a row and does not change the other fields. A new row removes the choice. The weights are counted from these rows when a choice is stored.

## model_choice

| Column | Rule |
|---|---|
| id | Integer, increases by 1 |
| task_id | One choice for the task |
| context | Trimmed context name |
| model | `linear` or `neural` |
| arm | Trimmed arm name that was chosen |
| recorded_at | The time the choice was stored |

One row replaces the previous choice. The scores are counted from the pulls when the choice is stored. Opening the task does not count them again.
