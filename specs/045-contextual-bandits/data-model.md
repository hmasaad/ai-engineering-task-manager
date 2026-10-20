# Data Model: Contextual Bandits and Reinforcement Learning for Workflow Scheduling

No column is added to an existing table.

## bandit_action

| Field | Rule |
|---|---|
| id | Integer primary key |
| task_id | Required. References `task(id)` |
| name | Required. Trimmed text, length greater than 0. Unique with `task_id` |
| recorded_at | Required timestamp |

A task holds at most 2 rows. Oldest first is `id` ascending.

## bandit_context

| Field | Rule |
|---|---|
| id | Integer primary key |
| task_id | Required. References `task(id)` |
| name | Required. Trimmed text, length greater than 0. Unique with `task_id` |
| recorded_at | Required timestamp |

A task holds at most 4 rows. Oldest first is `id` ascending.

## bandit_trial

| Field | Rule |
|---|---|
| id | Integer primary key |
| task_id | Required. References `task(id)` |
| name | Required. Trimmed text, length greater than 0. Unique with `task_id` |
| context_id | Required. References `bandit_context(id)` |
| action_id | Required. References `bandit_action(id)` |
| reward | Required integer. One of 1 or 2 |
| recorded_at | Required timestamp |

A task holds at most 4 rows. Oldest first is `id` ascending.

## Learned value

A learned value is not a separate table. It is each distinct pair of context and action among the trials of one task. Oldest pair first is the pair of the earliest trial, then the next new pair. The total is the sum of that pair's rewards. The count is the number of trials in that pair. The average is that total divided by that count. One average is higher than another when its total multiplied by the other count is greater than the other total multiplied by its count.

## bandit_choice

| Field | Rule |
|---|---|
| id | Integer primary key |
| task_id | Required. Unique. References `task(id)` |
| context_id | Required. References `bandit_context(id)` |
| action_id | Required. References `bandit_action(id)` |
| recorded_at | Required timestamp |

One task has one stored choice. A later choice replaces it. A new action, a new context, or a new trial removes it.
