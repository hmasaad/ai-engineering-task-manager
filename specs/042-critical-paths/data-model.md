# Data Model: Workflow Scheduling with Dependencies, Critical Paths, and Deadline Propagation

No column is added to an existing table. Latest times and the critical path are derived from these rows.

## path_step

| Field | Rule |
|---|---|
| id | Integer primary key |
| task_id | Required. References `task(id)` |
| name | Required. Trimmed text, length greater than 0. Unique with `task_id` |
| length | Required integer. One of 1 or 2 |
| recorded_at | Required timestamp |

Oldest first is `id` ascending. A length of 1 is one day. A length of 2 is two days.

## path_link

| Field | Rule |
|---|---|
| id | Integer primary key |
| task_id | Required. References `task(id)` |
| step_id | Required. Unique. References `path_step(id)` |
| predecessor_id | Required. References `path_step(id)`. Different from `step_id` |
| recorded_at | Required timestamp |

One step has at most one predecessor. A link that reaches its own step by walking predecessors is a cycle and is not stored.

## path_deadline

| Field | Rule |
|---|---|
| id | Integer primary key |
| task_id | Required. Unique. References `task(id)` |
| deadline | Required text. A real UTC time in the form `2026-12-03T00:00:00Z` |
| recorded_at | Required timestamp |

One task has one deadline. A new deadline replaces the stored text.

## Critical path

A chain starts at a step that follows nothing and continues through each step that follows the previous one. The critical path is the chain with the greatest sum of lengths. Equal sums choose the chain whose first step has the smallest `path_step.id`. The path is listed from that first step to the last.

## Latest time

The last step of every chain finishes at `deadline`. Walking backward, each earlier step finishes earlier by the length, in days, of the steps after it.
