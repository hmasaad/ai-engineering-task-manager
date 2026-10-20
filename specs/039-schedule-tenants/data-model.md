# Data Model: Multi-Tenant Workflow Scheduling, Fairness, and Resource Quotas

No column is added to an existing table. Turns used are the count of `schedule_turn` rows for that tenant.

## schedule_tenant

| Field | Rule |
|---|---|
| id | Integer primary key |
| task_id | Required. References `task(id)` |
| name | Required. Trimmed text, length greater than 0. Unique with `task_id` |
| quota | Required integer. Stored as 2 |
| recorded_at | Required timestamp |

Oldest first is `id` ascending.

## schedule_turn

| Field | Rule |
|---|---|
| id | Integer primary key |
| task_id | Required. References `task(id)` |
| name | Required. Trimmed text, length greater than 0. Unique with `task_id` |
| tenant_id | Required. References `schedule_tenant(id)` |
| recorded_at | Required timestamp |

Oldest first is `id` ascending. A tenant's used count is the number of these rows for that `tenant_id`.

## Choice

The chosen tenant is an admitted tenant on that task whose used count is below `quota`, with the smallest used count. Equal counts choose the smallest `schedule_tenant.id`.
