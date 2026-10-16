# Implementation Plan: Workflow Replay and Deterministic Execution

**Branch**: `026-deterministic-replay` | **Date**: 2026-10-16 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/026-deterministic-replay/spec.md`

## Summary

Replaying execution walks the current workflow version and matches each completed step to the file read or folder change already stored. The same stored workflow returns the same report. The walk does not perform a step.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI, Uvicorn, Jinja2, pytest. SQLite through `sqlite3`. No new dependency.

**Storage**: The existing SQLite workspace file. No new table. The report is derived from the current version, its steps, file reads, and folder changes.

**Testing**: pytest. Unit tests cover a finished workflow, a pending step, a missing effect, and a waiting step. A contract test covers the page. Existing feature tests stay green.

**Target Platform**: Local machine. The server binds to `127.0.0.1` only.

**Project Type**: Local web application with a domain library in the same process

**Performance Goals**: One replay reads the stored rows for one task and writes nothing.

**Constraints**: One engineer, no sign-in. Constitution v1.0.0. Specifications 001 through 025 are not rewritten. `GET /api/tasks` stays the top-level task list. Replay does not call the clock and does not call the model.

**Scale/Scope**: One engineer and one workspace file. One report per request.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution: `.specify/memory/constitution.md` v1.0.0.

### Before research

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | The spec names the matched effect and the stop sentences. |
| II. Test-first verification | Pass | The spec says the rules are covered by automated checks. This phase produces no application code. |
| III. Explicit task state | Pass | Replay does not change the task status or a step state. |
| IV. Traceability | Pass | Each matched step names the stored effect. |
| V. Deterministic behavior | Pass | The same stored rows produce the same report. |
| VI. Observable AI actions | Pass | Replay does not perform an action and does not rewrite the replay. |
| VII. Human approval | Pass | A waiting step stays waiting. Replay does not approve it. |
| VIII. Small, independently verifiable changes | Pass | One derived report. |

No gate failed.

### After design

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | [data-model.md](data-model.md) names the report. |
| II. Test-first verification | Pass | [quickstart.md](quickstart.md) names the tests that must pass. |
| III. Explicit task state | Pass | [research.md](research.md) keeps replay free of writes. |
| IV. Traceability | Pass | [contracts/commands.md](contracts/commands.md) names the effect on each matched step. |
| V. Deterministic behavior | Pass | A repeated command returns the same report. |
| VI. Observable AI actions | Pass | The event replay is unchanged. |
| VII. Human approval | Pass | Waiting stays `waiting for approval.` |
| VIII. Small, independently verifiable changes | Pass | No new table. |

No gate failed after design. No exception is requested.

## Project Structure

### Documentation (this feature)

```text
specs/026-deterministic-replay/
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
├── workspace.py
├── web/api.py
├── web/pages.py
└── web/templates/detail.html

tests/
├── unit/test_deterministic_replay.py
└── contract/test_deterministic_replay_api.py
```

**Structure Decision**: The report is computed from stored rows in the workflow domain. The page and the command share that computation. No schema change is required.
