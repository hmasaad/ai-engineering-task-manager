# Implementation Plan: Replay a Dead Letter

**Branch**: `035-replay-dead-letter` | **Date**: 2026-10-19 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/035-replay-dead-letter/spec.md`

## Summary

The engineer names a replay. The oldest dead letter that has not been replayed is shown as Pending again and can be delivered. The dead letter remains. A rolled-back replay leaves the message Dead.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI, Uvicorn, Jinja2, pytest. SQLite through `sqlite3`. No new dependency.

**Storage**: The existing SQLite workspace file. One new table, `workflow_dead_letter_replay`. No column is added to an existing table. `workflow_outbox.state` stays `Pending` or `Delivered`. Dead-letter rows are not deleted.

**Testing**: pytest. Unit tests cover one replay, a second dead letter, a rolled-back replay, an unchanged attempt count, and a delivery before the old next time. A contract test covers the page. Existing feature tests stay green.

**Target Platform**: Local machine. The server binds to `127.0.0.1` only.

**Project Type**: Local web application with a domain library in the same process

**Performance Goals**: One request replays one dead letter or delivers one message.

**Constraints**: One engineer, no sign-in. Constitution v1.0.0. Specifications 001 through 034 are not rewritten. `GET /api/tasks` stays the top-level task list. A Refusal rolls its own transaction back. Replay does not reset the attempt count.

**Scale/Scope**: One engineer and one workspace file. One replay per request.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution: `.specify/memory/constitution.md` v1.0.0.

### Before research

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | The spec names the replay and the sentences. |
| II. Test-first verification | Pass | The spec says the rules are covered by automated checks. This phase produces no application code. |
| III. Explicit task state | Pass | A replay exists only after an accepted name. |
| IV. Traceability | Pass | The replay names the dead letter that was returned. |
| V. Deterministic behavior | Pass | The oldest unreplayed dead letter is the one returned. |
| VI. Observable AI actions | Pass | The task shows the replay. |
| VII. Human approval | Pass | Replay does not create or delete a project file. |
| VIII. Small, independently verifiable changes | Pass | One new table. The dead letter stays. |

No gate failed.

### After design

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | [data-model.md](data-model.md) names the replay. |
| II. Test-first verification | Pass | [quickstart.md](quickstart.md) names the tests that must pass. |
| III. Explicit task state | Pass | [research.md](research.md) shows the message as Pending only after a replay. |
| IV. Traceability | Pass | [contracts/commands.md](contracts/commands.md) returns the name and the message. |
| V. Deterministic behavior | Pass | The same name does not return a second message. |
| VI. Observable AI actions | Pass | The page lists each replay. |
| VII. Human approval | Pass | Replay does not deliver the message by itself. |
| VIII. Small, independently verifiable changes | Pass | The outbox state check is unchanged. |

No gate failed after design. No exception is requested.

## Project Structure

### Documentation (this feature)

```text
specs/035-replay-dead-letter/
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
├── unit/test_replay_dead_letter.py
└── contract/test_replay_dead_letter_api.py
```

**Structure Decision**: The replay is a new row that points at the dead letter. Delivery includes a replayed message and still skips a dead letter that has no replay.
