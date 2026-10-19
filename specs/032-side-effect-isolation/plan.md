# Implementation Plan: Deterministic Replay and Side-Effect Isolation

**Branch**: `032-side-effect-isolation` | **Date**: 2026-10-19 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/032-side-effect-isolation/spec.md`

## Summary

A completed step seals the file or folder it stored, in the same result as the completion. Replay matches those seals and does not open the project, even after the file or folder has been removed.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI, Uvicorn, Jinja2, pytest. SQLite through `sqlite3`. No new dependency.

**Storage**: The existing SQLite workspace file. One new table, `workflow_isolated_effect`. No column is added to an existing table.

**Testing**: pytest. Unit tests cover the seal, a rolled-back completion, and a replay after the file and the folder are removed. A contract test covers the page. Existing feature tests stay green.

**Target Platform**: Local machine. The server binds to `127.0.0.1` only.

**Project Type**: Local web application with a domain library in the same process

**Performance Goals**: One completion seals one effect. One replay reads the seals and writes nothing.

**Constraints**: One engineer, no sign-in. Constitution v1.0.0. Specifications 001 through 031 are not rewritten. `GET /api/tasks` stays the top-level task list. A Refusal rolls its own transaction back. The replay does not call the clock and does not touch the project directory.

**Scale/Scope**: One engineer and one workspace file. One seal or one replay per request.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution: `.specify/memory/constitution.md` v1.0.0.

### Before research

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | The spec names the seal and the stop sentences. |
| II. Test-first verification | Pass | The spec says the rules are covered by automated checks. This phase produces no application code. |
| III. Explicit task state | Pass | A seal exists only for a completed step. |
| IV. Traceability | Pass | The seal names the step and the file or folder. |
| V. Deterministic behavior | Pass | A second replay returns the same report. |
| VI. Observable AI actions | Pass | Replay does not perform the step. |
| VII. Human approval | Pass | Replay does not create or delete a project file. |
| VIII. Small, independently verifiable changes | Pass | One new table. The existing execution replay stays. |

No gate failed.

### After design

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | [data-model.md](data-model.md) names the sealed effect. |
| II. Test-first verification | Pass | [quickstart.md](quickstart.md) names the tests that must pass. |
| III. Explicit task state | Pass | [research.md](research.md) seals the effect only when the step is Completed. |
| IV. Traceability | Pass | [contracts/commands.md](contracts/commands.md) returns the sealed path. |
| V. Deterministic behavior | Pass | Replay does not call the clock. |
| VI. Observable AI actions | Pass | A removed file stays removed. |
| VII. Human approval | Pass | Replay writes nothing in the project. |
| VIII. Small, independently verifiable changes | Pass | One seal per completed step. |

No gate failed after design. No exception is requested.

## Project Structure

### Documentation (this feature)

```text
specs/032-side-effect-isolation/
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
├── storage/workflow_store.py
├── storage/schema.sql
├── workspace.py
├── web/api.py
├── web/pages.py
└── web/templates/detail.html

tests/
├── unit/test_side_effect_isolation.py
└── contract/test_side_effect_isolation_api.py
```

**Structure Decision**: The seal is stored with the completion. Replay reads that table and does not open the project.
