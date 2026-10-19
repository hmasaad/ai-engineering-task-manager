# Implementation Plan: Run One File Read

**Branch**: `036-run-file-read` | **Date**: 2026-10-19 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/036-run-file-read/spec.md`

## Summary

The engineer names a run. The next workflow step is performed only when it reads a file, and that file read is stored the same way an advance of the step stores it. The same name does not perform another step. A rolled-back run leaves the step pending.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI, Uvicorn, Jinja2, pytest. SQLite through `sqlite3`. No new dependency.

**Storage**: The existing SQLite workspace file. One new table, `workflow_file_run`. No column is added to an existing table. `workflow_advance` is not used for this name.

**Testing**: pytest. Unit tests cover one read, a second read, a folder that is left pending, a rolled-back run, a missing file, and another task. A contract test covers the page. Existing feature tests stay green.

**Target Platform**: Local machine. The server binds to `127.0.0.1` only.

**Project Type**: Local web application with a domain library in the same process

**Performance Goals**: One request runs one file-read step.

**Constraints**: One engineer, no sign-in. Constitution v1.0.0. Specifications 001 through 035 are not rewritten. `GET /api/tasks` stays the top-level task list. A Refusal rolls its own transaction back. The read and the run name commit together, so a rollback leaves the step Pending.

**Scale/Scope**: One engineer and one workspace file. One run per request.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution: `.specify/memory/constitution.md` v1.0.0.

### Before research

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | The spec names the run and the sentences. |
| II. Test-first verification | Pass | The spec says the rules are covered by automated checks. This phase produces no application code. |
| III. Explicit task state | Pass | A run exists only after an accepted name performs a read. |
| IV. Traceability | Pass | The run names the file-read step it performed. |
| V. Deterministic behavior | Pass | The next unfinished file-read step is the one performed. |
| VI. Observable AI actions | Pass | The task shows the run and the stored file read. |
| VII. Human approval | Pass | A folder, an approval, a delivery, a commit, and a pull request stay for the engineer. |
| VIII. Small, independently verifiable changes | Pass | One new table. Advance workflow stays. |

No gate failed.

### After design

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | [data-model.md](data-model.md) names the run. |
| II. Test-first verification | Pass | [quickstart.md](quickstart.md) names the tests that must pass. |
| III. Explicit task state | Pass | [research.md](research.md) stores the name only after the step is performed. |
| IV. Traceability | Pass | [contracts/commands.md](contracts/commands.md) returns the name and the step. |
| V. Deterministic behavior | Pass | The same name does not perform a second step. |
| VI. Observable AI actions | Pass | The page lists each run. |
| VII. Human approval | Pass | The run refuses a step that is not a file read. |
| VIII. Small, independently verifiable changes | Pass | The advance name table is unchanged. |

No gate failed after design. No exception is requested.

## Project Structure

### Documentation (this feature)

```text
specs/036-run-file-read/
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
├── domain/workflow.py
├── storage/schema.sql
├── storage/workflow_store.py
├── web/api.py
├── web/pages.py
├── web/templates/detail.html
└── workspace.py

tests/unit/test_run_file_read.py
tests/contract/test_run_file_read_api.py
```

**Structure Decision**: The existing single-project layout. The run is a domain command beside advance, with one new table.
