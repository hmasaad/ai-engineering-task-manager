# Implementation Plan: Dead Letter Queues and Poison Messages

**Branch**: `029-dead-letter-queue` | **Date**: 2026-10-16 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/029-dead-letter-queue/spec.md`

## Summary

The engineer rejects the oldest Pending outbox message by name and reason. The third rejection of that message stores a dead letter. Delivery skips a dead letter and continues with the next Pending message.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI, Uvicorn, Jinja2, pytest. SQLite through `sqlite3`. No new dependency.

**Storage**: The existing SQLite workspace file. Two new tables, `workflow_poison` and `workflow_dead_letter`. No column is added to an existing table. The outbox state check is not changed.

**Testing**: pytest. Unit tests cover the third rejection, a repeated name, and a rolled-back rejection. A contract test covers the page. Existing feature tests stay green.

**Target Platform**: Local machine. The server binds to `127.0.0.1` only.

**Project Type**: Local web application with a domain library in the same process

**Performance Goals**: One request records one rejection. The third rejection also stores one dead letter.

**Constraints**: One engineer, no sign-in. Constitution v1.0.0. Specifications 001 through 028 are not rewritten. `GET /api/tasks` stays the top-level task list. A Refusal rolls its own transaction back. Three rejections are the fixed limit.

**Scale/Scope**: One engineer and one workspace file. One rejection per request.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution: `.specify/memory/constitution.md` v1.0.0.

### Before research

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | The spec names the third rejection and the sentences. |
| II. Test-first verification | Pass | The spec says the rules are covered by automated checks. This phase produces no application code. |
| III. Explicit task state | Pass | A message is Pending, Delivered, or a dead letter. |
| IV. Traceability | Pass | Each rejection names the message and the reason. |
| V. Deterministic behavior | Pass | The oldest Pending message that is not a dead letter is the next one. |
| VI. Observable AI actions | Pass | Rejection does not run a step. |
| VII. Human approval | Pass | A dead letter stays on record. Nothing stored is deleted. |
| VIII. Small, independently verifiable changes | Pass | Two new tables. |

No gate failed.

### After design

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | [data-model.md](data-model.md) names the rejection and the dead letter. |
| II. Test-first verification | Pass | [quickstart.md](quickstart.md) names the tests that must pass. |
| III. Explicit task state | Pass | [research.md](research.md) shows a dead letter without changing the outbox check. |
| IV. Traceability | Pass | [contracts/commands.md](contracts/commands.md) stores the name and the reason with the message. |
| V. Deterministic behavior | Pass | Delivery and rejection share the same oldest-message rule. |
| VI. Observable AI actions | Pass | The original outbox message remains. |
| VII. Human approval | Pass | The dead letter is kept with its reason. |
| VIII. Small, independently verifiable changes | Pass | One rejection per request. |

No gate failed after design. No exception is requested.

## Project Structure

### Documentation (this feature)

```text
specs/029-dead-letter-queue/
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
├── unit/test_dead_letter.py
└── contract/test_dead_letter_api.py
```

**Structure Decision**: A poison rejection and a dead letter are stored beside the outbox message. The outbox row is not deleted and its stored state check is not changed.
