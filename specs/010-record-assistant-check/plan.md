# Implementation Plan: Record One Check by the Assistant

**Branch**: `010-record-assistant-check` | **Date**: 2026-10-12 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/010-record-assistant-check/spec.md`

## Summary

On an In Progress task, the engineer submits one check the assistant has already produced. The check names one carried-out change, one acceptance criterion on that task, the evidence, and Passed or Failed. The product stores that check and the workspace assistant. It does not call a model, open a file, verify a criterion, record a decision, or change the task status. The check counts under the existing passing-check rule. The engineer's own check command stays unchanged and does not name an assistant.

The work extends the existing Python process. One new table only. No new dependency, and no new task status.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI, Uvicorn, Jinja2, pytest. SQLite through `sqlite3`. No new dependency.

**Storage**: The same SQLite workspace file. One new table links an existing implementation check to the workspace assistant. `implementation_check` is not altered. An engineer-recorded check has no row in the new table.

**Testing**: pytest. Unit tests cover one rule at a time. Contract tests cover the HTTP command. One integration test records an assistant check and reads it back without storing a second check. Existing engineer-check and completion tests stay green.

**Target Platform**: Local machine. The server binds to `127.0.0.1` only.

**Project Type**: Local web application with a domain library in the same process

**Performance Goals**: Recording one assistant check and opening the task that holds it each finish in under 200 milliseconds on a workspace of 5,000 tasks and 5,000 checks. The assistant name is read by the check's primary key. Completion keeps today's per-change lookup and does not scan every check for an assistant name.

**Constraints**: One workspace, no sign-in, no model call, and no project file. The client cannot choose the assistant name, the engineer name, or the time. Constitution v1.0.0. Specifications 001 through 009 are not rewritten.

**Scale/Scope**: One engineer and one workspace. This feature adds one assistant check on one carried-out change. It does not add a task status, a requirement run, a decision, or a file write.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution: `.specify/memory/constitution.md` v1.0.0.

### Before research

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | The spec names the assistant, the change, the criterion, the evidence, Passed or Failed, and the refusals. |
| II. Test-first verification | Pass | This phase produces no application code. |
| III. Explicit task state | Pass | Task status stays Draft, Ready, In Progress, Completed, or Cancelled. Recording the check does not transition the task. |
| IV. Traceability | Pass | The check names the change and the criterion. It counts under the existing passing-check rule. |
| V. Deterministic behavior | Pass | The product stores the submitted result. It does not call a model or open a file. Replay reads the stored check. |
| VI. Observable AI actions | Pass | The stored check names the workspace assistant, the evidence, the result, and the time. |
| VII. Human approval | Pass | The check does not delete or overwrite durable data. A later check can replace the current result. Verifying a criterion, deciding, approving, completing, and cancelling stay with the engineer. |
| VIII. Small, independently verifiable changes | Pass | One workspace feature. It does not run tests, create folders, or rewrite earlier specifications. |

No gate failed.

### After design

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | [data-model.md](data-model.md) and the contracts restate the guard order, the assistant name, and the unchanged engineer check. |
| II. Test-first verification | Pass | [quickstart.md](quickstart.md) requires failing tests before the behavior is done, including one rule alone and a replay that stores no second check. |
| III. Explicit task state | Pass | [research.md](research.md) reuses the existing check insert. No status is added. |
| IV. Traceability | Pass | The new row points at one implementation check. The task detail lists that check with the assistant. |
| V. Deterministic behavior | Pass | The current result stays the latest check by time, then by id. Opening the task does not insert a row. |
| VI. Observable AI actions | Pass | The API ignores a client-supplied assistant name, engineer name, and time. An engineer check has no assistant name. |
| VII. Human approval | Pass | [contracts/http-api.md](contracts/http-api.md) does not add an approval step for the check. Approve, decline, verify, decide, complete, and cancel stay the existing engineer commands. |
| VIII. Small, independently verifiable changes | Pass | The task page and the API call the same domain function. The existing check command writes no assistant row. |

No gate failed after design. No exception is requested.

## Project Structure

### Documentation (this feature)

```text
specs/010-record-assistant-check/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
└── tasks.md
```

### Source Code (repository root)

```text
src/task_manager/
├── domain/verification.py       # assistant check reuses the existing guard order
├── storage/schema.sql
├── storage/verification_store.py
├── storage/task_store.py        # a decision's check object includes the assistant name
├── workspace.py
└── web/
    ├── api.py
    ├── pages.py
    └── templates/
        └── detail.html

tests/
├── unit/test_assistant_check.py
├── contract/test_assistant_check_api.py
└── integration/test_replay.py
```

**Structure Decision**: Extend `src/task_manager`. The domain module is the only writer of the assistant check. Pages and the API call that module. Storage does not decide whether a check is passing. Existing feature 003 checks stay on the same table and gain an assistant name only when this command stored one.

## Complexity Tracking

No constitution violations require justification.
