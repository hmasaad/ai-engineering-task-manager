# Implementation Plan: Task Dependencies

**Branch**: `019-task-dependencies` | **Date**: 2026-10-14 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/019-task-dependencies/spec.md`

## Summary

A task can name another task as a prerequisite. Self-links, unknown tasks, and cycles are refused. One reading lists every task so that each prerequisite comes first, with the lower id first when several tasks could come next. Starting is refused while any prerequisite is not Completed, and the refusal names the incomplete status or the unverified criteria. The Ready status is unchanged.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI, Uvicorn, Jinja2, pytest. SQLite through `sqlite3`. No new dependency.

**Storage**: The existing SQLite workspace file. One new table, `task_dependency`. No new column on `task`.

**Testing**: pytest. Unit tests cover one link, one order, or one start hold. Contract tests cover the commands. Existing feature tests stay green.

**Target Platform**: Local machine. The server binds to `127.0.0.1` only.

**Project Type**: Local web application with a domain library in the same process

**Performance Goals**: The execution order for 5,000 tasks finishes in under 200 milliseconds. The order is one read of the tasks and one read of the links.

**Constraints**: One engineer, no sign-in. Constitution v1.0.0. Specifications 001 through 018 are not rewritten. `GET /api/tasks` stays the top-level task list.

**Scale/Scope**: One engineer and one workspace file per start. One prerequisite per request. One order for the whole workspace.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution: `.specify/memory/constitution.md` v1.0.0.

### Before research

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | The spec names the link, the refusals, the order, and the start hold. |
| II. Test-first verification | Pass | The spec says the rules are covered by automated checks. This phase produces no application code. |
| III. Explicit task state | Pass | Statuses stay Draft, Ready, In Progress, Completed, and Cancelled. Ready is not redefined. |
| IV. Traceability | Pass | A prerequisite is a stored link between two tasks. The start refusal names that task. |
| V. Deterministic behavior | Pass | The order breaks ties by the lower id. Reading it does not change a status. |
| VI. Observable AI actions | Pass | The engineer names the prerequisite. The product does not infer a link from a subtask. |
| VII. Human approval | Pass | Adding a link does not start, complete, or cancel a task. |
| VIII. Small, independently verifiable changes | Pass | Three stories. Specifications 001 through 018 are not rewritten. |

No gate failed.

### After design

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | [data-model.md](data-model.md) names `task_dependency` and the blocked sentence. |
| II. Test-first verification | Pass | [quickstart.md](quickstart.md) names the tests that must pass. |
| III. Explicit task state | Pass | [research.md](research.md) leaves mark Ready, complete, and cancel unchanged. |
| IV. Traceability | Pass | [contracts/commands.md](contracts/commands.md) stores one prerequisite id on one task. |
| V. Deterministic behavior | Pass | The order uses the stored links and the lower id. |
| VI. Observable AI actions | Pass | A subtask link does not insert a prerequisite. |
| VII. Human approval | Pass | The start hold does not carry out another task. |
| VIII. Small, independently verifiable changes | Pass | One table, one order read, and one check before start. |

No gate failed after design. No exception is requested.

## Project Structure

### Documentation (this feature)

```text
specs/019-task-dependencies/
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
├── domain/dependency.py
├── domain/status.py
├── storage/schema.sql
├── storage/dependency_store.py
├── storage/task_store.py
├── web/api.py
├── web/pages.py
├── web/templates/detail.html
├── web/templates/list.html
└── workspace.py

tests/unit/test_dependency.py
tests/contract/test_dependency_api.py
```

**Structure Decision**: A new domain module and a new store. Start calls the blocked sentence. The task page and the task list render the link and the order.
