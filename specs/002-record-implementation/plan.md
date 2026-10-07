# Implementation Plan: Record Task Implementation

**Branch**: `002-record-implementation` | **Date**: 2026-10-07 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/002-record-implementation/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

An engineer attaches an implementation change to an In Progress task: what changed, whether it is ordinary or consequential, and which task it serves. An ordinary change is carried out when it is saved. A consequential change stays Awaiting approval until a later command approves it with the evidence reviewed, or marks it not carried out with a reason. Neither command changes task status, criteria, or decisions. Completing or cancelling a task is refused while any change on that task is Awaiting approval, and the refusal names each waiting change.

The work stays in the existing Python 3.12 process. New domain rules and two append-only tables sit beside the task record from feature 001. The task detail page and the JSON API call those rules. Research is in [research.md](research.md).

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI, Uvicorn, Jinja2, pytest. SQLite through the standard-library `sqlite3` driver. No new dependency.

**Storage**: The same SQLite workspace file. Two new tables: one insert-only change row, and at most one insert-only resolution row per change.

**Testing**: pytest. Domain tests call the rules directly. Contract tests call the HTTP commands with FastAPI's test client. The existing scripted clock supplies timestamps.

**Target Platform**: Local machine. The server binds to `127.0.0.1` only.

**Project Type**: Local web application with a domain library in the same process

**Performance Goals**: Each new command, and completion or cancellation with the added guard, completes in under 200 milliseconds on a workspace of 5,000 tasks and 5,000 implementation changes.

**Constraints**: No sign-in, no assistant actor, no file list, no review link, no edit or delete of a saved change or resolution. The client cannot choose the engineer name or the time. Recording, approving, and marking not carried out do not change task status. Constitution v1.0.0.

**Scale/Scope**: One engineer and one workspace. The existing task list and task detail pages. This feature adds the change list and three actions on the detail page.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution: `.specify/memory/constitution.md` v1.0.0.

### Before research

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | The spec names the engineer, ordinary and consequential changes, the three outcomes, and pass/fail scenarios for every story, including the 2026-10-07 completion rule. |
| II. Test-first verification | Pass | This phase produces no application code. Implementation is not started until tests exist for the scenario they prove. |
| III. Explicit task state | Pass | Task status stays the five stored statuses. A change outcome is a stored class plus an optional stored resolution, not a guess from the wording. |
| IV. Traceability | Pass | Each change names one task. An approval names that change and the evidence reviewed. |
| V. Deterministic behavior | Pass | The same commands must yield the same outcomes and order. The existing clock remains the only time source. |
| VI. Observable AI actions | Pass | This feature has no assistant command. There is no agent action to hide. |
| VII. Human approval | Pass | A consequential change is not carried out by saving it. Approval is a separate command that names the change and the evidence. Silence is not approval. |
| VIII. Small, independently verifiable changes | Pass | The three stories can be tested on their own. The plan does not add accounts, sharing, or an assistant. |

No gate failed. Research records how this feature uses the existing process. It does not relax a rule.

### After design

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | [data-model.md](data-model.md) and the contracts restate the spec guards, including the completion and cancel refusal. They do not add a behavior the spec does not name. |
| II. Test-first verification | Pass | [quickstart.md](quickstart.md) requires failing tests mapped to spec scenarios before a behavior is done. |
| III. Explicit task state | Pass | Task status is unchanged by these commands. Outcome is defined from the stored class and the stored resolution row. |
| IV. Traceability | Pass | `implementation_change.task_id` and `implementation_resolution.change_id` keep the chain. The engineer name and time are copied onto each row. |
| V. Deterministic behavior | Pass | [research.md](research.md) reuses the injected clock and orders changes by `recorded_at`, then `id`. |
| VI. Observable AI actions | Pass | The API ignores a client-supplied engineer name and exposes no assistant route. |
| VII. Human approval | Pass | Approve and mark-not-carried-out are separate HTTP actions. A refused command commits nothing. There is no delete. |
| VIII. Small, independently verifiable changes | Pass | One process. The detail page calls the same functions as the API. Stories map to separate quickstart scenarios. |

No gate failed after design. No exception is requested.

## Project Structure

### Documentation (this feature)

```text
specs/002-record-implementation/
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
├── domain/
│   ├── implementation.py  # record, approve, mark not carried out
│   └── status.py          # complete and cancel also refuse waiting changes
├── storage/
│   ├── schema.sql         # implementation_change, implementation_resolution
│   └── implementation_store.py
└── web/
    ├── api.py             # new commands
    └── templates/detail.html

tests/
├── unit/test_implementation.py
├── contract/test_implementation_api.py
└── integration/test_replay.py   # same script twice, including these commands
```

**Structure Decision**: Extend `src/task_manager`. The new domain module does not import the web framework. Storage is the only writer of the new tables. `status.py` asks the implementation rules whether any change on that task is still Awaiting approval before it completes or cancels. The detail page and the JSON API call the same functions. Tests are split so a rule can fail in `tests/unit` without a server, and a contract mismatch fails in `tests/contract`.

## Complexity Tracking

No constitution violations require justification.
