# Data Model: Safe Exploration, Causal Inference, and Counterfactual Evaluation

No column is added to an existing table.

## safe_action

| Field | Rule |
|---|---|
| id | Integer primary key |
| task_id | Required. References `task(id)` |
| name | Required. Trimmed text, length greater than 0. Unique with `task_id` |
| risk | Required integer. One of 1 or 2 |
| recorded_at | Required timestamp |

A task holds at most 2 rows. Oldest first is `id` ascending. A risk of 1 is safe to explore. A risk of 2 is not safe to explore.

## safe_probe

| Field | Rule |
|---|---|
| id | Integer primary key |
| task_id | Required. References `task(id)` |
| name | Required. Trimmed text, length greater than 0. Unique with `task_id` |
| state | Required. Trimmed text, length greater than 0 |
| action_id | Required. References `safe_action(id)` |
| reward | Required integer. One of 1 or 2 |
| recorded_at | Required timestamp |

A task holds at most 4 rows. The referenced action must have risk 1. Oldest first is `id` ascending. A new row removes the effect.

## safe_effect

| Field | Rule |
|---|---|
| id | Integer primary key |
| task_id | Required. Unique. References `task(id)` |
| state | Required. Trimmed text, length greater than 0 |
| action | Required. Trimmed text, length greater than 0 |
| instead | Required. Trimmed text, length greater than 0. It differs from `action` |
| effect | Required integer. The reward difference, from -1 through 1 |
| recorded_at | Required timestamp |

One comparison replaces the effect. For the named action, the reward is the reward of the earliest probe of that action in `state`. The same rule gives the reward of `instead`. The effect is the first reward minus the second. A new action or a new probe removes the effect.
