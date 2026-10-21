# Data Model: Adaptive Resource Allocation for Workflow and Agent Optimization

## allocation_agent

| Column | Rule |
|---|---|
| id | Integer, increases by 1 |
| task_id | The task that owns the agent |
| name | Trimmed text, unique with the task |
| recorded_at | The time the agent was stored |

A task holds at most 4 rows. Rows are read oldest id first. The same name does not add a row. A new row removes the shares.

## allocation_yield

| Column | Rule |
|---|---|
| id | Integer, increases by 1 |
| task_id | The task that owns the yield |
| name | Trimmed text, unique with the task |
| agent_id | The agent on this task, unique with the task |
| value | 1 or 2 |
| recorded_at | The time the yield was stored |

A task holds at most 4 rows. An agent has at most one row. The same name does not add a row and does not change the other fields. A new row removes the shares.

## allocation_share

| Column | Rule |
|---|---|
| id | Integer, increases by 1 |
| task_id | The task that owns the share |
| agent | Trimmed agent name |
| units | Whole number from 0 through 4 |
| position | 1 or greater, in agent order |
| recorded_at | The time the allocation was stored |

One allocation replaces the previous shares. The units for a task add up to 4. They are read by position. Opening the task does not count them again.
