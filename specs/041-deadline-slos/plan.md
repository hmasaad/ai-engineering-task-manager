# Implementation Plan: Deadline-Aware Scheduling and Service-Level Objectives (SLOs)

**Branch**: `041-deadline-slos` | **Date**: 2026-10-20 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/041-deadline-slos/spec.md`

## Summary

The engineer names an objective on an In Progress task and gives it a UTC deadline. A named service goes to the waiting objective with the earliest deadline. The objective named first wins a tie. The service is recorded as met when its recorded time is at or before the deadline, and as missed when it is after.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI, Uvicorn, Jinja2, pytest. SQLite through `sqlite3`. No new dependency.

**Storage**: The existing SQLite workspace file. Two new tables, `slo_objective` and `slo_service`. No column is added to an existing table.

**Testing**: pytest. Unit tests cover a deadline, an earliest-deadline service, a met result, a missed result, a rolled-back service, and another task. A contract test covers the page. Existing feature tests stay green.

**Target Platform**: Local machine. The server binds to `127.0.0.1` only.

**Project Type**: Local web application with a domain library in the same process

**Performance Goals**: One request sets one objective or serves one objective.

**Constraints**: One engineer, no sign-in. Constitution v1.0.0. Specifications 001 through 040 are not rewritten. `GET /api/tasks` stays the top-level task list. A Refusal rolls its own transaction back. A service and its met or missed result commit together.

**Scale/Scope**: One engineer and one workspace file. One command per request. A deadline is one UTC timestamp.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution: `.specify/memory/constitution.md` v1.0.0.

### Before research

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | The spec names the deadline form, the earliest deadline, and the refusal sentences. |
| II. Test-first verification | Pass | The spec says the rules are covered by automated checks. This phase produces no application code. |
| III. Explicit task state | Pass | A deadline and a met or missed service are stored rows. Waiting is an objective with no service. |
| IV. Traceability | Pass | A service names the objective it served and the result. |
| V. Deterministic behavior | Pass | The earliest deadline and the earliest objective are fixed by stored text and storage order. The clock is stored with the service. |
| VI. Observable AI actions | Pass | The task shows each waiting deadline and each met or missed service. |
| VII. Human approval | Pass | The commands do not approve, deliver, commit, or open a pull request. |
| VIII. Small, independently verifiable changes | Pass | Two new tables. Priority, tenants, workers, and the workflow stay as they are. |

No gate failed.

### After design

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | [data-model.md](data-model.md) names the objective and the service. |
| II. Test-first verification | Pass | [quickstart.md](quickstart.md) names the tests that must pass. |
| III. Explicit task state | Pass | [research.md](research.md) stores met or missed on the service. |
| IV. Traceability | Pass | [contracts/commands.md](contracts/commands.md) returns the objective and the result on each service. |
| V. Deterministic behavior | Pass | Equal deadlines choose the objective stored first. A later page open does not recompute the result. |
| VI. Observable AI actions | Pass | The page lists waiting objectives and services. |
| VII. Human approval | Pass | The commands refuse to change the task status. |
| VIII. Small, independently verifiable changes | Pass | No existing table is altered. |

No gate failed after design. No exception is requested.

## Project Structure

### Documentation (this feature)

```text
specs/041-deadline-slos/
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
├── domain/slo.py
├── storage/schema.sql
├── storage/slo_store.py
├── storage/task_store.py
├── workspace.py
├── web/api.py
├── web/pages.py
└── web/templates/detail.html

tests/unit/test_deadline_slos.py
tests/contract/test_deadline_slos_api.py
```

**Structure Decision**: The existing single-project layout. Objectives and services are a new deadline schedule beside the priority commands, with two new tables.
