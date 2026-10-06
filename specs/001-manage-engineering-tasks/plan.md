# Implementation Plan: Manage Engineering Tasks

**Branch**: `001-manage-engineering-tasks` | **Date**: 2026-10-06 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-manage-engineering-tasks/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Engineers keep a local workspace of tasks with a goal, acceptance criteria, explicit status, subtasks, and implementation decisions. A task is completed only when every criterion has an engineer-named observation, an explicit pass, and a time, and every direct subtask is Completed or Cancelled. Cancelled is final. Reopening a Completed task returns it and every Completed ancestor to In Progress without clearing existing verifications.

The implementation is one Python 3.12 process: a domain module that owns the rules, a SQLite file for the workspace, and a localhost web UI. Research for the stack, clock, and identity choices is in [research.md](research.md).

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI, Uvicorn, Jinja2, pytest. SQLite through the standard-library `sqlite3` driver.

**Storage**: One SQLite file per workspace

**Testing**: pytest. Domain tests call the rules directly. Contract tests call the HTTP commands with FastAPI's test client. A scripted clock is injected in tests.

**Target Platform**: Local machine. The server binds to `127.0.0.1` only.

**Project Type**: Local web application with a domain library in the same process

**Performance Goals**: Each command completes in under 200 milliseconds on a workspace of 5,000 tasks, so the spec's human times (create a task in under 3 minutes, add a subtask in under 2 minutes) are not limited by the application.

**Constraints**: No sign-in, no assistant actor, no delete of tasks or decisions, no inferred status change. The clock is injected and the time used for a transition is stored with that transition. Nesting depth is not capped. Cycles are refused. Constitution v1.0.0.

**Scale/Scope**: One engineer and one workspace. Planning ceiling of 5,000 tasks. Two pages: the task list and the task detail.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution: `.specify/memory/constitution.md` v1.0.0.

### Before research

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | The spec names the engineer, the outcomes, and pass/fail scenarios for every story. |
| II. Test-first verification | Pass | This phase produces no application code. Implementation is not started until tests exist for the scenario they prove. |
| III. Explicit task state | Pass | The spec's five statuses and the closed transition list are the only legal states. |
| IV. Traceability | Pass | Criteria, history, and decisions stay attached to one task. Verification stores observation, pass, time, and provider. |
| V. Deterministic behavior | Pass | The same commands must yield the same statuses and order. How the clock is isolated is a research decision, not an open product rule. |
| VI. Observable AI actions | Pass | This feature has no assistant command. There is no agent action to hide. |
| VII. Human approval | Pass | Complete, cancel, reopen, start, and verify are explicit engineer actions. Silence does not approve them. |
| VIII. Small, independently verifiable changes | Pass | The four user stories can be tested on their own. The plan does not add accounts, notifications, or an assistant. |

No gate failed. Research proceeded to choose the stack, not to relax a rule.

### After design

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | [data-model.md](data-model.md) and the contracts restate the spec guards. They do not add a behavior the spec does not name. |
| II. Test-first verification | Pass | [quickstart.md](quickstart.md) requires failing tests mapped to spec scenarios before a behavior is done. |
| III. Explicit task state | Pass | `status` is a stored column. Every change appends a `status_change` row with from, to, time, and cause. |
| IV. Traceability | Pass | Criterion, status change, and decision rows reference the task. Verified criteria carry the evidence fields. Ancestor updates are separate history rows in the same transaction. |
| V. Deterministic behavior | Pass | [research.md](research.md) isolates the clock and orders rows by stored time, then integer id. |
| VI. Observable AI actions | Pass | The API rejects a client-supplied provider and exposes no assistant route. |
| VII. Human approval | Pass | Consequential commands are separate HTTP actions. A refused command commits nothing. There is no delete. |
| VIII. Small, independently verifiable changes | Pass | One process. Pages call the same functions as the API. Stories map to separate quickstart scenarios. |

No gate failed after design. No exception is requested.

## Project Structure

### Documentation (this feature)

```text
specs/001-manage-engineering-tasks/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
src/task_manager/
├── domain/              # statuses, guards, transitions
├── storage/             # SQLite workspace
├── web/                 # localhost pages and HTTP commands
└── __main__.py          # process entry

tests/
├── unit/                # domain rules and refusals
├── integration/         # workspace file and replay
└── contract/            # HTTP commands against the contracts
```

**Structure Decision**: One Python package under `src/task_manager`. The domain module does not import the web framework. Storage is the only writer of the SQLite file. The web package renders the two pages and the JSON commands, and both call the domain. Tests are split so a rule can fail in `tests/unit` without a server, and a contract mismatch fails in `tests/contract`.

## Complexity Tracking

No constitution violations require justification.
