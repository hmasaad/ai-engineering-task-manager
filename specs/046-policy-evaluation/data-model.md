# Data Model: Offline Reinforcement Learning and Policy Evaluation

No column is added to an existing table.

## eval_log

| Field | Rule |
|---|---|
| id | Integer primary key |
| task_id | Required. References `task(id)` |
| name | Required. Trimmed text, length greater than 0. Unique with `task_id` |
| state | Required. Trimmed text, length greater than 0 |
| action | Required. Trimmed text, length greater than 0 |
| reward | Required integer. One of 1 or 2 |
| recorded_at | Required timestamp |

A task holds at most 4 rows. Oldest first is `id` ascending. A reward of 1 is a weak result. A reward of 2 is a strong result.

## eval_rule

| Field | Rule |
|---|---|
| id | Integer primary key |
| task_id | Required. References `task(id)` |
| state | Required. Trimmed text. Unique with `task_id`. It must match the state of a logged step on this task |
| action | Required. Trimmed text, length greater than 0 |
| recorded_at | Required timestamp |

One state has one row. A different action replaces `action` and removes the score. Oldest first is `id` ascending.

## eval_score

| Field | Rule |
|---|---|
| id | Integer primary key |
| task_id | Required. Unique. References `task(id)` |
| total | Required integer, 0 or greater. The sum of the rewards of the matching logged steps |
| count | Required integer, 1 or greater. The number of matching logged steps |
| recorded_at | Required timestamp |

One evaluation replaces the score. A logged step matches when its state equals a rule's state and its action equals that rule's action. A logged step whose state has no rule is left out. A new logged step or a changed rule removes the score.
