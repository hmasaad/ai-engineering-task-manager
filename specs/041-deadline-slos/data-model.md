# Data Model: Deadline-Aware Scheduling and Service-Level Objectives (SLOs)

No column is added to an existing table. Waiting objectives are `slo_objective` rows that no `slo_service` row points at.

## slo_objective

| Field | Rule |
|---|---|
| id | Integer primary key |
| task_id | Required. References `task(id)` |
| name | Required. Trimmed text, length greater than 0. Unique with `task_id` |
| deadline | Required text. A real UTC time in the form `2026-12-01T00:00:00Z` |
| recorded_at | Required timestamp |

Oldest first is `id` ascending.

## slo_service

| Field | Rule |
|---|---|
| id | Integer primary key |
| task_id | Required. References `task(id)` |
| name | Required. Trimmed text, length greater than 0. Unique with `task_id` |
| objective_id | Required. References `slo_objective(id)` |
| result | Required text. One of `met` or `missed` |
| recorded_at | Required timestamp |

Oldest first is `id` ascending. One service points at one objective. An objective that a service points at is not waiting.

## Choice

The chosen objective is waiting on that task with the smallest `deadline`. Equal deadlines choose the smallest `slo_objective.id`.

`result` is `met` when `recorded_at` is at or before `deadline`, and `missed` when `recorded_at` is after `deadline`. Both values are written in the same form, so text order matches time order. A repeated service name stores nothing.
