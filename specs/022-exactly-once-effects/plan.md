# Implementation Plan: Idempotency and Exactly-Once Effects

**Branch**: `022-exactly-once-effects` | **Date**: 2026-10-14 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/022-exactly-once-effects/spec.md`

## Summary

A workflow step stores one file read or one folder change. Finishing or advancing that step again uses the stored effect and does not perform the action. A Failed step with no stored effect can still be retried. An advance name remembers the step it performed. The same name does not perform another step. The task page supplies a new name each time the task is shown.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI, Uvicorn, Jinja2, pytest. SQLite through `sqlite3`. No new dependency.

**Storage**: The existing SQLite workspace file. One new table, `workflow_advance`. No new column on `task` or `workflow_step`.

**Testing**: pytest. Unit tests cover a stored effect and a repeated advance name. Contract tests cover the command and the task page. Existing feature tests stay green.

**Target Platform**: Local machine. The server binds to `127.0.0.1` only.

**Project Type**: Local web application with a domain library in the same process

**Performance Goals**: A repeated advance name is one lookup and returns without performing a step. The lookup finishes in under 200 milliseconds.

**Constraints**: One engineer, no sign-in. Constitution v1.0.0. Specifications 001 through 021 are not rewritten. `GET /api/tasks` stays the top-level task list. A blank advance name is not stored, so existing unnamed advances keep their current behavior. A Refusal still rolls its own transaction back.

**Scale/Scope**: One engineer and one workspace file per start. One named or unnamed advance per request.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution: `.specify/memory/constitution.md` v1.0.0.

### Before research

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | The spec names one effect per step and one result per advance name. |
| II. Test-first verification | Pass | The spec says the rules are covered by automated checks. This phase produces no application code. |
| III. Explicit task state | Pass | Task statuses stay unchanged. A repeated name does not move a step. |
| IV. Traceability | Pass | The advance name remembers the step it was for. |
| V. Deterministic behavior | Pass | The same name on the same task returns without a second effect. |
| VI. Observable AI actions | Pass | A second finish uses the stored effect instead of performing the action. |
| VII. Human approval | Pass | A declined folder change is not recorded again. Approval stays the existing command. |
| VIII. Small, independently verifiable changes | Pass | Three stories. The workflow actions stay Read a file and Create a folder. |

No gate failed.

### After design

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | [data-model.md](data-model.md) names `workflow_advance`. |
| II. Test-first verification | Pass | [quickstart.md](quickstart.md) names the tests that must pass. |
| III. Explicit task state | Pass | [research.md](research.md) leaves the task status unchanged. |
| IV. Traceability | Pass | [contracts/commands.md](contracts/commands.md) ties one name to one step. |
| V. Deterministic behavior | Pass | The same trimmed name is one row. A repeat does not write a replay entry. |
| VI. Observable AI actions | Pass | Finish applies a stored effect before it would perform the action. |
| VII. Human approval | Pass | A Failed step that already has its change is not performed again. |
| VIII. Small, independently verifiable changes | Pass | One new table and an optional name on the existing advance. |

No gate failed after design. No exception is requested.

## Project Structure

### Documentation (this feature)

```text
specs/022-exactly-once-effects/
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
├── unit/test_exactly_once.py
└── contract/test_exactly_once_api.py
```

**Structure Decision**: The effect check and the advance name live in `domain/workflow.py`. Pages and the API call the same workspace method. A blank name keeps the current advance path.
