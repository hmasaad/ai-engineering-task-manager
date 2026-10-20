# Data Model: Priority Scheduling, Aging, and Starvation Prevention

No column is added to an existing table. Waiting work is a `priority_work` row that no `priority_serve` row points at.

## priority_work

| Field | Rule |
|---|---|
| id | Integer primary key |
| task_id | Required. References `task(id)` |
| name | Required. Trimmed text, length greater than 0. Unique with `task_id` |
| rank | Required integer. One of 1, 2, or 3 |
| age | Required integer. Stored as 0. Greater than or equal to 0 |
| recorded_at | Required timestamp |

Oldest first is `id` ascending. The score of waiting work is `rank` plus `age`.

## priority_serve

| Field | Rule |
|---|---|
| id | Integer primary key |
| task_id | Required. References `task(id)` |
| name | Required. Trimmed text, length greater than 0. Unique with `task_id` |
| work_id | Required. References `priority_work(id)` |
| recorded_at | Required timestamp |

Oldest first is `id` ascending. One serve points at one piece of work. Work that a serve points at is not waiting.

## Choice

The chosen work is waiting work on that task with the largest `rank + age`. Equal scores choose the smallest `priority_work.id`.

When that serve is stored, every other waiting row on the same task has `age` increased by 1. The chosen row does not age. A repeated serve name stores nothing and changes no age.
