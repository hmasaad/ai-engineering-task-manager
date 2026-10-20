# Commands: Multi-Tenant Workflow Scheduling, Fairness, and Resource Quotas

## Admit tenant

`POST /api/tasks/{task_id}/tenants`

`POST /tasks/{task_id}/tenants`

```json
{ "name": "ada" }
```

`name` may be omitted. The page field is Tenant name, `id="tenant-name"`. The button is Admit tenant.

The trimmed name is stored once with a quota of 2 and zero turns used. The same name returns the task detail and does not admit another tenant.

## Grant turn

`POST /api/tasks/{task_id}/turns`

`POST /tasks/{task_id}/turns`

```json
{ "name": "one" }
```

`name` may be omitted. The page field is Turn name, `id="turn-name"`. The button is Grant turn.

The trimmed name is stored once. The turn is granted to the tenant who has used the fewest turns and is still under 2. Equal counts choose the tenant stored first. The same name returns the task detail and does not grant another turn.

## Task detail

The task detail includes `schedule`:

```json
{
  "tenants": [
    { "name": "ada", "used": 1, "quota": 2 }
  ],
  "turns": [
    { "name": "one", "tenant": "ada" }
  ],
  "can_admit": true,
  "can_grant": true
}
```

`tenants` and `turns` are oldest first. `can_admit` is true while the task is In Progress. `can_grant` is true while the task is In Progress and a tenant has used fewer than 2 turns.

## Page

The task page shows a Schedule section.

- Each tenant is `ada: 1 of 2` in `id="tenants"`.
- Each turn is `one granted to ada` in `id="turns"`.
- Admit tenant is offered while the task is In Progress.
- Grant turn is offered only while `can_grant` is true.

## Refusals

| Condition | Status | Message |
|---|---|---|
| Blank tenant name | 400 | `Name this tenant.` |
| Blank turn name | 400 | `Name this turn.` |
| No tenant admitted | 409 | `Name a tenant first.` |
| Every tenant has used 2 turns | 409 | `Every tenant is at its quota.` |
| Task is not In Progress | 409 | `The task must be In Progress.` |
| Task is missing | 404 | `Task not found.` |

A repeated tenant name or turn name returns the task detail with status 200.
