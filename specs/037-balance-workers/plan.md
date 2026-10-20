# Implementation Plan: Work Stealing, Backpressure, and Load Balancing

**Branch**: `037-balance-workers` | **Date**: 2026-10-20 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/037-balance-workers/spec.md`

## Summary

The engineer names workers on an In Progress task and places jobs. A job goes to the worker with the fewest pending jobs, and the worker named first wins a tie. A worker already holding three pending jobs does not take another. An idle worker can be named in a steal that takes the oldest job from the busiest other worker.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI, Uvicorn, Jinja2, pytest. SQLite through `sqlite3`. No new dependency.

**Storage**: The existing SQLite workspace file. Three new tables, `work_worker`, `work_job`, and `work_steal`. No column is added to an existing table.

**Testing**: pytest. Unit tests cover load balancing, a full queue, a rolled-back placement, a steal, a rolled-back steal, and another task. A contract test covers the page. Existing feature tests stay green.

**Target Platform**: Local machine. The server binds to `127.0.0.1` only.

**Project Type**: Local web application with a domain library in the same process

**Performance Goals**: One request adds one worker, places one job, or steals one job.

**Constraints**: One engineer, no sign-in. Constitution v1.0.0. Specifications 001 through 036 are not rewritten. `GET /api/tasks` stays the top-level task list. A Refusal rolls its own transaction back. The job and the steal name commit together, so a rollback leaves the job on its original worker.

**Scale/Scope**: One engineer and one workspace file. One command per request. The bound is three pending jobs.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution: `.specify/memory/constitution.md` v1.0.0.

### Before research

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | The spec names the workers, the bound, and the sentences. |
| II. Test-first verification | Pass | The spec says the rules are covered by automated checks. This phase produces no application code. |
| III. Explicit task state | Pass | A job is pending and names the worker who holds it. |
| IV. Traceability | Pass | A steal names the job and both workers. |
| V. Deterministic behavior | Pass | Ties go to the worker named first. The stolen job is the oldest. |
| VI. Observable AI actions | Pass | The task shows the workers, the jobs, and the steals. |
| VII. Human approval | Pass | The commands do not approve, deliver, commit, or open a pull request. |
| VIII. Small, independently verifiable changes | Pass | Three new tables. Workflow steps stay as they are. |

No gate failed.

### After design

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | [data-model.md](data-model.md) names the worker, the job, and the steal. |
| II. Test-first verification | Pass | [quickstart.md](quickstart.md) names the tests that must pass. |
| III. Explicit task state | Pass | [research.md](research.md) stores a job only after a worker can take it. |
| IV. Traceability | Pass | [contracts/commands.md](contracts/commands.md) returns the job and the workers. |
| V. Deterministic behavior | Pass | Equal counts choose the earliest worker. |
| VI. Observable AI actions | Pass | The page lists each worker and each steal. |
| VII. Human approval | Pass | The commands refuse to change the task status. |
| VIII. Small, independently verifiable changes | Pass | No existing table is altered. |

No gate failed after design. No exception is requested.

## Project Structure

### Documentation (this feature)

```text
specs/037-balance-workers/
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
├── storage/task_store.py
├── workspace.py
├── web/api.py
├── web/pages.py
└── web/templates/detail.html

tests/unit/test_balance_workers.py
tests/contract/test_balance_workers_api.py
```

**Structure Decision**: The existing single-project layout. Workers are a domain command beside the workflow, with three new tables.
