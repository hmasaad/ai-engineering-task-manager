# Implementation Plan: Multi-Tenant Workflow Scheduling, Fairness, and Resource Quotas

**Branch**: `039-schedule-tenants` | **Date**: 2026-10-20 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/039-schedule-tenants/spec.md`

## Summary

The engineer admits named tenants to an In Progress task. Each tenant may take two turns. A named turn is granted to the tenant who has used the fewest turns and is still under that quota. The tenant admitted first wins a tie.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI, Uvicorn, Jinja2, pytest. SQLite through `sqlite3`. No new dependency.

**Storage**: The existing SQLite workspace file. Two new tables, `schedule_tenant` and `schedule_turn`. No column is added to an existing table.

**Testing**: pytest. Unit tests cover an admission, a fair grant, a full quota, a rolled-back turn, and another task. A contract test covers the page. Existing feature tests stay green.

**Target Platform**: Local machine. The server binds to `127.0.0.1` only.

**Project Type**: Local web application with a domain library in the same process

**Performance Goals**: One request admits one tenant or grants one turn.

**Constraints**: One engineer, no sign-in. Constitution v1.0.0. Specifications 001 through 038 are not rewritten. `GET /api/tasks` stays the top-level task list. A Refusal rolls its own transaction back. A turn and the tenant who receives it commit together.

**Scale/Scope**: One engineer and one workspace file. One command per request. Each tenant may take two turns.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution: `.specify/memory/constitution.md` v1.0.0.

### Before research

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | The spec names the quota of two and the refusal sentences. |
| II. Test-first verification | Pass | The spec says the rules are covered by automated checks. This phase produces no application code. |
| III. Explicit task state | Pass | A tenant and a turn are stored rows. Turns used are the turns stored for that tenant. |
| IV. Traceability | Pass | A turn names the tenant who received it. |
| V. Deterministic behavior | Pass | The fewest turns and the earliest tenant are fixed by storage order. |
| VI. Observable AI actions | Pass | The task shows each tenant and each granted turn. |
| VII. Human approval | Pass | The commands do not approve, deliver, commit, or open a pull request. |
| VIII. Small, independently verifiable changes | Pass | Two new tables. Workers and the workflow stay as they are. |

No gate failed.

### After design

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | [data-model.md](data-model.md) names the tenant and the turn. |
| II. Test-first verification | Pass | [quickstart.md](quickstart.md) names the tests that must pass. |
| III. Explicit task state | Pass | [research.md](research.md) counts turns from stored rows. |
| IV. Traceability | Pass | [contracts/commands.md](contracts/commands.md) returns the tenant on each turn. |
| V. Deterministic behavior | Pass | Equal counts choose the tenant stored first. |
| VI. Observable AI actions | Pass | The page lists tenants and granted turns. |
| VII. Human approval | Pass | The commands refuse to change the task status. |
| VIII. Small, independently verifiable changes | Pass | No existing table is altered. |

No gate failed after design. No exception is requested.

## Project Structure

### Documentation (this feature)

```text
specs/039-schedule-tenants/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── commands.md
└── tasks.md
```

### Source Code (repository root)

```text
src/task_manager/
├── domain/schedule.py
├── storage/schema.sql
├── storage/schedule_store.py
├── storage/task_store.py
├── workspace.py
├── web/api.py
├── web/pages.py
└── web/templates/detail.html

tests/unit/test_schedule_tenants.py
tests/contract/test_schedule_tenants_api.py
```

**Structure Decision**: The existing single-project layout. Tenants and turns are a new schedule beside the worker commands, with two new tables.
