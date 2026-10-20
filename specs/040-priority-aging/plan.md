# Implementation Plan: Priority Scheduling, Aging, and Starvation Prevention

**Branch**: `040-priority-aging` | **Date**: 2026-10-20 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/040-priority-aging/spec.md`

## Summary

The engineer ranks named work on an In Progress task at 1, 2, or 3. A named serve goes to the waiting work with the highest score, where the score is rank plus age. The work ranked first wins a tie. Every other piece still waiting ages by 1. Rank-1 work aged by 2 ties a new rank of 3 and is served first.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI, Uvicorn, Jinja2, pytest. SQLite through `sqlite3`. No new dependency.

**Storage**: The existing SQLite workspace file. Two new tables, `priority_work` and `priority_serve`. No column is added to an existing table.

**Testing**: pytest. Unit tests cover a rank, a highest-score serve, aging, a starvation tie, a rolled-back serve, and another task. A contract test covers the page. Existing feature tests stay green.

**Target Platform**: Local machine. The server binds to `127.0.0.1` only.

**Project Type**: Local web application with a domain library in the same process

**Performance Goals**: One request ranks one piece of work or serves one piece of work.

**Constraints**: One engineer, no sign-in. Constitution v1.0.0. Specifications 001 through 039 are not rewritten. `GET /api/tasks` stays the top-level task list. A Refusal rolls its own transaction back. A serve and the age of the other waiting work commit together.

**Scale/Scope**: One engineer and one workspace file. One command per request. Ranks are 1, 2, and 3.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution: `.specify/memory/constitution.md` v1.0.0.

### Before research

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | The spec names the ranks, the score, and the refusal sentences. |
| II. Test-first verification | Pass | The spec says the rules are covered by automated checks. This phase produces no application code. |
| III. Explicit task state | Pass | Rank, age, and a serve are stored rows. Waiting work is work with no serve. |
| IV. Traceability | Pass | A serve names the work it served. |
| V. Deterministic behavior | Pass | The highest score and the earliest work are fixed by stored rank, age, and storage order. Aging does not read the clock. |
| VI. Observable AI actions | Pass | The task shows each waiting rank and age, and each serve. |
| VII. Human approval | Pass | The commands do not approve, deliver, commit, or open a pull request. |
| VIII. Small, independently verifiable changes | Pass | Two new tables. Tenants, workers, and the workflow stay as they are. |

No gate failed.

### After design

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | [data-model.md](data-model.md) names the ranked work and the serve. |
| II. Test-first verification | Pass | [quickstart.md](quickstart.md) names the tests that must pass. |
| III. Explicit task state | Pass | [research.md](research.md) stores age on the work and waiting as the absence of a serve. |
| IV. Traceability | Pass | [contracts/commands.md](contracts/commands.md) returns the work on each serve. |
| V. Deterministic behavior | Pass | Equal scores choose the work stored first. Age rises by 1 only when a new serve is stored. |
| VI. Observable AI actions | Pass | The page lists waiting work and serves. |
| VII. Human approval | Pass | The commands refuse to change the task status. |
| VIII. Small, independently verifiable changes | Pass | No existing table is altered. |

No gate failed after design. No exception is requested.

## Project Structure

### Documentation (this feature)

```text
specs/040-priority-aging/
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
├── domain/priority.py
├── storage/schema.sql
├── storage/priority_store.py
├── storage/task_store.py
├── workspace.py
├── web/api.py
├── web/pages.py
└── web/templates/detail.html

tests/unit/test_priority_aging.py
tests/contract/test_priority_aging_api.py
```

**Structure Decision**: The existing single-project layout. Ranked work and serves are a new priority schedule beside the tenant commands, with two new tables.
