# Implementation Plan: Transactional Outbox and Inbox

**Branch**: `027-transactional-outbox` | **Date**: 2026-10-16 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/027-transactional-outbox/spec.md`

## Summary

Completing a workflow step stores one outbox message in that same result. The engineer delivers the oldest Pending message by name. The inbox records that name once, and a repeated name does not deliver another message.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI, Uvicorn, Jinja2, pytest. SQLite through `sqlite3`. No new dependency.

**Storage**: The existing SQLite workspace file. New tables `workflow_outbox` and `workflow_inbox`. No column is added to an existing table.

**Testing**: pytest. Unit tests cover one message per completed step, a rolled-back completion, and a delivery name accepted once. A contract test covers the page. Existing feature tests stay green.

**Target Platform**: Local machine. The server binds to `127.0.0.1` only.

**Project Type**: Local web application with a domain library in the same process

**Performance Goals**: Completion writes one outbox row. One delivery accepts one message.

**Constraints**: One engineer, no sign-in. Constitution v1.0.0. Specifications 001 through 026 are not rewritten. `GET /api/tasks` stays the top-level task list. A Refusal still rolls its own transaction back, including any outbox row written in that transaction.

**Scale/Scope**: One engineer and one workspace file. One completion or one delivery per request.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution: `.specify/memory/constitution.md` v1.0.0.

### Before research

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | The spec names one message per completed step and one acceptance per delivery name. |
| II. Test-first verification | Pass | The spec says the rules are covered by automated checks. This phase produces no application code. |
| III. Explicit task state | Pass | A message is Pending or Delivered. Delivery does not change the task status. |
| IV. Traceability | Pass | The message names the step and the stored file or folder. |
| V. Deterministic behavior | Pass | The oldest Pending message is the one a new name delivers. |
| VI. Observable AI actions | Pass | Delivery does not perform the step. |
| VII. Human approval | Pass | Delivery does not approve a waiting change. |
| VIII. Small, independently verifiable changes | Pass | One outbox and one inbox. |

No gate failed.

### After design

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | [data-model.md](data-model.md) names the two records. |
| II. Test-first verification | Pass | [quickstart.md](quickstart.md) names the tests that must pass. |
| III. Explicit task state | Pass | [research.md](research.md) leaves task status unchanged. |
| IV. Traceability | Pass | [contracts/commands.md](contracts/commands.md) stores the step effect on the message. |
| V. Deterministic behavior | Pass | A repeated name returns the same inbox entry. |
| VI. Observable AI actions | Pass | The file read or folder change stays the one the step already stored. |
| VII. Human approval | Pass | A waiting step stores no message. |
| VIII. Small, independently verifiable changes | Pass | Two new tables. |

No gate failed after design. No exception is requested.

## Project Structure

### Documentation (this feature)

```text
specs/027-transactional-outbox/
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
├── unit/test_transactional_outbox.py
└── contract/test_transactional_outbox_api.py
```

**Structure Decision**: The outbox row is inserted beside the completed step in the same transaction. The inbox row is inserted beside the delivery that accepts one message.
