# Implementation Plan: Idempotency and Duplicate Execution Control

**Branch**: `033-duplicate-execution` | **Date**: 2026-10-19 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/033-duplicate-execution/spec.md`

## Summary

The engineer can name a Read a file or Create a folder command. The first accepted use of that name on a task performs the command once. The same name afterward returns the task and does not perform it again.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI, Uvicorn, Jinja2, pytest. SQLite through `sqlite3`. No new dependency.

**Storage**: The existing SQLite workspace file. One new table, `command_execution`. No column is added to an existing table.

**Testing**: pytest. Unit tests cover a repeated read, a repeated folder, a refusal that leaves the name free, and a rolled-back command. A contract test covers the page. Existing feature tests stay green.

**Target Platform**: Local machine. The server binds to `127.0.0.1` only.

**Project Type**: Local web application with a domain library in the same process

**Performance Goals**: One named command stores one execution. A repeated name writes nothing new.

**Constraints**: One engineer, no sign-in. Constitution v1.0.0. Specifications 001 through 032 are not rewritten. `GET /api/tasks` stays the top-level task list. A Refusal rolls its own transaction back. A workflow step does not record a command execution. A blank name is not saved.

**Scale/Scope**: One engineer and one workspace file. One command or one repeated name per request.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution: `.specify/memory/constitution.md` v1.0.0.

### Before research

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | The spec names the command, the path, and the refusal sentence. |
| II. Test-first verification | Pass | The spec says the rules are covered by automated checks. This phase produces no application code. |
| III. Explicit task state | Pass | An execution exists only after an accepted command. |
| IV. Traceability | Pass | The execution names the task, the command, and the path. |
| V. Deterministic behavior | Pass | The same name returns the earlier execution. |
| VI. Observable AI actions | Pass | The task lists the name and the path. |
| VII. Human approval | Pass | A repeated name does not create or delete a project file and does not approve a change. |
| VIII. Small, independently verifiable changes | Pass | One new table. Named workflow advances stay as they are. |

No gate failed.

### After design

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | [data-model.md](data-model.md) names the execution. |
| II. Test-first verification | Pass | [quickstart.md](quickstart.md) names the tests that must pass. |
| III. Explicit task state | Pass | [research.md](research.md) stores the name only after the command is accepted. |
| IV. Traceability | Pass | [contracts/commands.md](contracts/commands.md) returns the name, the command, and the path. |
| V. Deterministic behavior | Pass | A repeated name does not read or create again. |
| VI. Observable AI actions | Pass | The page lists each named execution. |
| VII. Human approval | Pass | A repeated consequential folder does not create the folder. |
| VIII. Small, independently verifiable changes | Pass | One execution per name on a task. |

No gate failed after design. No exception is requested.

## Project Structure

### Documentation (this feature)

```text
specs/033-duplicate-execution/
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
├── domain/execution.py
├── domain/file_read.py
├── domain/folder.py
├── storage/execution_store.py
├── storage/schema.sql
├── storage/task_store.py
├── workspace.py
├── web/api.py
├── web/pages.py
└── web/templates/detail.html

tests/
├── unit/test_duplicate_execution.py
└── contract/test_duplicate_execution_api.py
```

**Structure Decision**: The execution is stored in the same result as the accepted command. A repeated name returns the task before the command runs.
