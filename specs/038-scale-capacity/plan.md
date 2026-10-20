# Implementation Plan: Autoscaling and Queue-Based Capacity Planning

**Branch**: `038-scale-capacity` | **Date**: 2026-10-20 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/038-scale-capacity/spec.md`

## Summary

The engineer queues waiting work and names a capacity plan. The plan records how many workers are needed, one for every three waiting or held items. A named scale assigns the oldest waiting item when a worker has room, adds one worker when the queue is past that capacity, or releases the newest idle worker when the queue needs fewer.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI, Uvicorn, Jinja2, pytest. SQLite through `sqlite3`. No new dependency.

**Storage**: The existing SQLite workspace file. Four new tables, `work_queue`, `work_plan`, `work_scale`, and `work_release`. No column is added to an existing table.

**Testing**: pytest. Unit tests cover a plan, a fill, a scale-up, a scale-down, a rolled-back scale, and another task. A contract test covers the page. Existing feature tests stay green.

**Target Platform**: Local machine. The server binds to `127.0.0.1` only.

**Project Type**: Local web application with a domain library in the same process

**Performance Goals**: One request queues one item, records one plan, or scales once.

**Constraints**: One engineer, no sign-in. Constitution v1.0.0. Specifications 001 through 037 are not rewritten. `GET /api/tasks` stays the top-level task list. A Refusal rolls its own transaction back. A scale and the worker or job it changes commit together.

**Scale/Scope**: One engineer and one workspace file. One command per request. The bound stays three jobs on an active worker.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution: `.specify/memory/constitution.md` v1.0.0.

### Before research

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | The spec names the plan, the bound, and the sentences. |
| II. Test-first verification | Pass | The spec says the rules are covered by automated checks. This phase produces no application code. |
| III. Explicit task state | Pass | Waiting work, a plan, and a scale are stored rows. |
| IV. Traceability | Pass | A scale names the worker it added, filled, or released. |
| V. Deterministic behavior | Pass | The oldest waiting item and the newest idle worker are fixed by storage order. |
| VI. Observable AI actions | Pass | The task shows the queue, the plan, and the scale. |
| VII. Human approval | Pass | The commands do not approve, deliver, commit, or open a pull request. |
| VIII. Small, independently verifiable changes | Pass | Four new tables. Direct placement still refuses a full worker. |

No gate failed.

### After design

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | [data-model.md](data-model.md) names the queue, the plan, and the scale. |
| II. Test-first verification | Pass | [quickstart.md](quickstart.md) names the tests that must pass. |
| III. Explicit task state | Pass | [research.md](research.md) stores a release instead of deleting a worker. |
| IV. Traceability | Pass | [contracts/commands.md](contracts/commands.md) returns the plan and the scale. |
| V. Deterministic behavior | Pass | Spare room is filled before a worker is added. |
| VI. Observable AI actions | Pass | The page lists waiting work, plans, and scales. |
| VII. Human approval | Pass | The commands refuse to change the task status. |
| VIII. Small, independently verifiable changes | Pass | No existing table is altered. |

No gate failed after design. No exception is requested.

## Project Structure

### Documentation (this feature)

```text
specs/038-scale-capacity/
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
├── domain/workers.py
├── storage/schema.sql
├── storage/worker_store.py
├── workspace.py
├── web/api.py
├── web/pages.py
└── web/templates/detail.html

tests/unit/test_scale_capacity.py
tests/contract/test_scale_capacity_api.py
```

**Structure Decision**: The existing single-project layout. Capacity and scale are commands beside the worker commands, with four new tables.
