# Data Model: Distributed Bayesian Optimization and Decentralized Scheduling

## consensus_point

| Column | Rule |
|---|---|
| id | Integer, increases by 1 |
| task_id | The task that owns the point |
| name | Trimmed text, unique with the task |
| setting | 1 or 2 |
| recorded_at | The time the point was stored |

A task holds at most 4 rows. Rows are read oldest id first. The same name does not add a row and does not change the setting. A new row removes the agreement.

## consensus_node

| Column | Rule |
|---|---|
| id | Integer, increases by 1 |
| task_id | The task that owns the node |
| name | Trimmed text, unique with the task |
| recorded_at | The time the node was stored |

A task holds at most 2 rows. Rows are read oldest id first. The same name does not add a row. A new row removes the agreement.

## consensus_report

| Column | Rule |
|---|---|
| id | Integer, increases by 1 |
| task_id | The task that owns the report |
| name | Trimmed text, unique with the task |
| node_id | The node on this task |
| point_id | The point on this task |
| score | 1 or 2 |
| recorded_at | The time the report was stored |

A task holds at most 4 rows. A node has at most one row for each point, so `task_id`, `node_id`, and `point_id` are unique together. The same name does not add a row and does not change the other fields. The report count is checked before a repeated node and point. A new row removes the agreement.

## consensus_proposal

| Column | Rule |
|---|---|
| id | Integer, increases by 1 |
| task_id | The task that owns the suggestion |
| node | Trimmed node name |
| point | Trimmed point name |
| position | 1 or greater, in node order |
| recorded_at | The time the agreement was stored |

One row is stored for each node that suggests a point. The rows are read by position. Opening the task does not count them again.

## consensus_choice

| Column | Rule |
|---|---|
| id | Integer, increases by 1 |
| task_id | The task that owns the agreement, unique |
| point | Trimmed point name |
| node | Trimmed node name |
| suggestions | 1 or 2 |
| recorded_at | The time the agreement was stored |

One row is stored when the nodes agree. The point is the one suggested by the most nodes. The node is the earliest node that suggested it.
