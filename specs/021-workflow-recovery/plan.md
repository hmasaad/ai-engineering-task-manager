# Implementation Plan: Workflow Recovery and Replay

**Branch**: `021-workflow-recovery` | **Date**: 2026-10-14 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/021-workflow-recovery/spec.md`

## Summary

Each advance records a step as running, then records the result. The engineer can read that replay. A step left running reports that it was interrupted, and advance will not perform it. Recover marks it failed when no effect was stored, or completed or waiting from the stored file read or folder change, without performing the action again.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI, Uvicorn, Jinja2, pytest. SQLite through `sqlite3`. No new dependency.

**Storage**: The existing SQLite workspace file. `workflow_step.state` gains `Running` in the table created for a new workspace. Two new tables, `workflow_event` and `workflow_attempt`. No new column on `task` or `workflow_step`.

**Testing**: pytest. Unit tests cover the replay, an interrupted step, and a stored effect. Contract tests cover the commands. Existing feature tests stay green.

**Target Platform**: Local machine. The server binds to `127.0.0.1` only.

**Project Type**: Local web application with a domain library in the same process

**Performance Goals**: Reading the replay of 500 entries finishes in under 200 milliseconds. The read is one query.

**Constraints**: One engineer, no sign-in. Constitution v1.0.0. Specifications 001 through 020 are not rewritten. `GET /api/tasks` stays the top-level task list. The running record commits before the result, so an interrupted step remains running. A Refusal still rolls its own transaction back.

**Scale/Scope**: One engineer and one workspace file per start. One replay read, one recovery, or one advance per request.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution: `.specify/memory/constitution.md` v1.0.0.

### Before research

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | The spec names the replay, the interruption sentence, and recovery from a stored effect. |
| II. Test-first verification | Pass | The spec says the rules are covered by automated checks. This phase produces no application code. |
| III. Explicit task state | Pass | Task statuses stay unchanged. A step may be Running, and that state is stored. |
| IV. Traceability | Pass | Each replay entry names the step. Recovery uses the effect already stored for that step. |
| V. Deterministic behavior | Pass | The replay is a stored list. Reading it does not perform a step. |
| VI. Observable AI actions | Pass | The start and the result are both stored. |
| VII. Human approval | Pass | Recovery does not approve a waiting change. |
| VIII. Small, independently verifiable changes | Pass | Three stories. The workflow actions stay Read a file and Create a folder. |

No gate failed.

### After design

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | [data-model.md](data-model.md) names `workflow_event` and `workflow_attempt`. |
| II. Test-first verification | Pass | [quickstart.md](quickstart.md) names the tests that must pass. |
| III. Explicit task state | Pass | [research.md](research.md) leaves the task status unchanged. |
| IV. Traceability | Pass | [contracts/commands.md](contracts/commands.md) returns the replay in entry order. |
| V. Deterministic behavior | Pass | Replay is a read. The same workspace file returns the same entries. |
| VI. Observable AI actions | Pass | The running entry is stored before the result entry. |
| VII. Human approval | Pass | A stored consequential folder stays Waiting until the existing approval. |
| VIII. Small, independently verifiable changes | Pass | Two new tables and one recovery command. |

No gate failed after design. No exception is requested.

## Project Structure

### Documentation (this feature)

```text
specs/021-workflow-recovery/
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
├── web/api.py
├── web/pages.py
└── web/templates/detail.html

tests/
├── unit/test_workflow_recovery.py
└── contract/test_workflow_recovery_api.py
```

**Structure Decision**: Replay and recovery live in `domain/workflow.py`. The start of an advance commits before the result. Pages and the API call the same workspace methods.
