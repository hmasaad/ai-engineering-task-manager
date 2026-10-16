# Implementation Plan: Saga Pattern and Compensation

**Branch**: `028-saga-compensation` | **Date**: 2026-10-16 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/028-saga-compensation/spec.md`

## Summary

The current workflow is a saga. After a step fails, the engineer compensates completed steps from the latest backward. A file read is compensated immediately and the stored read remains. A created folder waits for approval before an empty folder is removed.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI, Uvicorn, Jinja2, pytest. SQLite through `sqlite3`. No new dependency.

**Storage**: The existing SQLite workspace file. One new table, `workflow_compensation`. No column is added to an existing table.

**Testing**: pytest. Unit tests cover reverse order, a rolled-back reason, and an empty folder that waits for approval. A contract test covers the page. Existing feature tests stay green.

**Target Platform**: Local machine. The server binds to `127.0.0.1` only.

**Project Type**: Local web application with a domain library in the same process

**Performance Goals**: One request compensates one step or settles one waiting compensation.

**Constraints**: One engineer, no sign-in. Constitution v1.0.0. Specifications 001 through 027 are not rewritten. `GET /api/tasks` stays the top-level task list. A Refusal rolls its own transaction back. Removing a folder happens only in the approval transaction.

**Scale/Scope**: One engineer and one workspace file. One compensation or one approval per request.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution: `.specify/memory/constitution.md` v1.0.0.

### Before research

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | The spec names reverse order and the folder approval. |
| II. Test-first verification | Pass | The spec says the rules are covered by automated checks. This phase produces no application code. |
| III. Explicit task state | Pass | The saga is Open, Failed, Waiting, or Compensated. |
| IV. Traceability | Pass | Each compensation names the step and the reason. |
| V. Deterministic behavior | Pass | The latest uncompensated completed step is the next one. |
| VI. Observable AI actions | Pass | Compensation does not run the step again. |
| VII. Human approval | Pass | Removing a folder waits for evidence reviewed. |
| VIII. Small, independently verifiable changes | Pass | One compensation record. |

No gate failed.

### After design

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | [data-model.md](data-model.md) names the compensation. |
| II. Test-first verification | Pass | [quickstart.md](quickstart.md) names the tests that must pass. |
| III. Explicit task state | Pass | [research.md](research.md) leaves the task status unchanged. |
| IV. Traceability | Pass | [contracts/commands.md](contracts/commands.md) stores the reason with the step. |
| V. Deterministic behavior | Pass | Reverse order is the completion order reversed. |
| VI. Observable AI actions | Pass | The stored file read and the original folder change remain. |
| VII. Human approval | Pass | A folder stays until approval. |
| VIII. Small, independently verifiable changes | Pass | One new table. |

No gate failed after design. No exception is requested.

## Project Structure

### Documentation (this feature)

```text
specs/028-saga-compensation/
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
├── unit/test_saga_compensation.py
└── contract/test_saga_compensation_api.py
```

**Structure Decision**: The compensation row is stored beside the step. Removing an empty folder happens only when that compensation is approved.
