# Implementation Plan: Bounded Delivery Retries

**Branch**: `034-bounded-retries` | **Date**: 2026-10-19 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/034-bounded-retries/spec.md`

## Summary

An unsuccessful delivery of a Pending outbox message records one attempt and a next time one minute later. A delivery before that time does nothing. The third attempt writes the existing dead letter and leaves the outbox state Pending.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI, Uvicorn, Jinja2, pytest. SQLite through `sqlite3`. No new dependency.

**Storage**: The existing SQLite workspace file. One new table, `workflow_delivery_retry`. No column is added to an existing table. `workflow_outbox.state` stays `Pending` or `Delivered`.

**Testing**: pytest. Unit tests cover an early delivery, a due delivery, the third attempt, a rolled-back third attempt, and a repeated name. A contract test covers the page. Existing feature tests stay green.

**Target Platform**: Local machine. The server binds to `127.0.0.1` only.

**Project Type**: Local web application with a domain library in the same process

**Performance Goals**: One request records one attempt or delivers one message.

**Constraints**: One engineer, no sign-in. Constitution v1.0.0. Specifications 001 through 033 are not rewritten. `GET /api/tasks` stays the top-level task list. A Refusal rolls its own transaction back. The bound is 3. The wait is one minute. A dead letter is not replayed.

**Scale/Scope**: One engineer and one workspace file. One attempt or one delivery per request.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution: `.specify/memory/constitution.md` v1.0.0.

### Before research

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | The spec names the bound, the wait, and the sentences. |
| II. Test-first verification | Pass | The spec says the rules are covered by automated checks. This phase produces no application code. |
| III. Explicit task state | Pass | An attempt exists only after an accepted unsuccessful delivery. |
| IV. Traceability | Pass | The attempt names the message and the next time. |
| V. Deterministic behavior | Pass | The next time is one minute after the workspace time of that attempt. |
| VI. Observable AI actions | Pass | The task shows the count and the next time. |
| VII. Human approval | Pass | An attempt does not create or delete a project file. |
| VIII. Small, independently verifiable changes | Pass | One new table. The existing dead letter is reused. |

No gate failed.

### After design

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | [data-model.md](data-model.md) names the attempt. |
| II. Test-first verification | Pass | [quickstart.md](quickstart.md) names the tests that must pass. |
| III. Explicit task state | Pass | [research.md](research.md) stops the count at three. |
| IV. Traceability | Pass | [contracts/commands.md](contracts/commands.md) returns the count and the next time. |
| V. Deterministic behavior | Pass | The wait uses the workspace clock. |
| VI. Observable AI actions | Pass | The page lists each attempt count. |
| VII. Human approval | Pass | The third attempt writes a dead letter and does not deliver. |
| VIII. Small, independently verifiable changes | Pass | The outbox state check is unchanged. |

No gate failed after design. No exception is requested.

## Project Structure

### Documentation (this feature)

```text
specs/034-bounded-retries/
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
├── unit/test_bounded_retries.py
└── contract/test_bounded_retries_api.py
```

**Structure Decision**: The attempt is stored with the unsuccessful delivery. The third attempt writes the existing dead letter in that same result.
