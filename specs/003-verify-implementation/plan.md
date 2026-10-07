# Implementation Plan: Verify a Recorded Change

**Branch**: `003-verify-implementation` | **Date**: 2026-10-07 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/003-verify-implementation/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

An engineer records a check of one carried-out implementation change against one acceptance criterion of the same In Progress task. The check stores the criterion wording at that time, the evidence, and an explicit result of Passed or Failed. Earlier checks stay. The current result of a change and a criterion is the latest check of that pair. The change has a passing check only when every criterion it has been checked against that still exists on the task has a current result of Passed. Completing the task is refused while any carried-out change on that task lacks a passing check, and the refusal names each such change. Cancellation is not refused for that reason. Recording a check does not change task status, the change outcome, or whether a criterion is Verified.

The work stays in the existing Python 3.12 process. A new append-only table and a new domain module sit beside the implementation record from feature 002. The task detail page and the JSON API call those rules. Research is in [research.md](research.md).

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI, Uvicorn, Jinja2, pytest. SQLite through the standard-library `sqlite3` driver. No new dependency.

**Storage**: The same SQLite workspace file. One new insert-only table, `implementation_check`, with many rows per change.

**Testing**: pytest. Domain tests call the rules directly. Contract tests call the HTTP commands with FastAPI's test client. The existing scripted clock supplies timestamps.

**Target Platform**: Local machine. The server binds to `127.0.0.1` only.

**Project Type**: Local web application with a domain library in the same process

**Performance Goals**: Recording a check, and completion with the added guard, completes in under 200 milliseconds on a workspace of 5,000 tasks, 5,000 implementation changes, and 5,000 checks.

**Constraints**: No sign-in, no assistant actor, no file list, no test runner, no review link, no edit or delete of a saved check. The client cannot choose the engineer name or the time. A check does not verify a criterion and does not change task status. A passing check requires every still-present checked criterion to be currently Passed. Constitution v1.0.0.

**Scale/Scope**: One engineer and one workspace. The existing task detail page. This feature adds the check list and one record-check action on each carried-out change.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution: `.specify/memory/constitution.md` v1.0.0.

### Before research

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | The spec names the engineer, the check, Passed and Failed, and pass/fail scenarios for every story, including the 2026-10-07 rule that every checked criterion must currently be Passed. |
| II. Test-first verification | Pass | This phase produces no application code. Implementation is not started until tests exist for the scenario they prove. |
| III. Explicit task state | Pass | Task status stays the five stored statuses. A check result is stored as Passed or Failed. The product does not infer it from the evidence. |
| IV. Traceability | Pass | Each check names one change and one acceptance criterion, and keeps that criterion's wording. The change already names the task. |
| V. Deterministic behavior | Pass | The same commands must yield the same results and order. The existing clock remains the only time source. |
| VI. Observable AI actions | Pass | This feature has no assistant command. There is no agent action to hide. |
| VII. Human approval | Pass | The engineer chooses Passed or Failed in an explicit command. Saving a change or approving it is not a check. Silence is not a pass. |
| VIII. Small, independently verifiable changes | Pass | The three stories can be tested on their own. The plan does not add accounts, sharing, a test runner, or an assistant. |

No gate failed. Research records how this feature uses the existing process. It does not relax a rule.

### After design

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | [data-model.md](data-model.md) and the contracts restate the spec guards, including the completion refusal and the rule that one current failure blocks a passing check. They do not add a behavior the spec does not name. |
| II. Test-first verification | Pass | [quickstart.md](quickstart.md) requires failing tests mapped to spec scenarios before a behavior is done. |
| III. Explicit task state | Pass | Task status is unchanged by recording a check. Passed and Failed are stored results. A passing check is defined from those rows and the criteria that still exist. |
| IV. Traceability | Pass | `implementation_check.change_id` and `criterion_id`, plus the copied criterion wording, keep the chain from task to change to requirement to evidence. |
| V. Deterministic behavior | Pass | [research.md](research.md) reuses the injected clock and orders checks by `checked_at`, then `id`. |
| VI. Observable AI actions | Pass | The API ignores a client-supplied engineer name and exposes no assistant route. |
| VII. Human approval | Pass | Record-check is its own HTTP action. A refused command commits nothing. There is no delete. Cancellation does not skip the completion guard. |
| VIII. Small, independently verifiable changes | Pass | One process. The detail page calls the same function as the API. Stories map to separate quickstart scenarios. |

No gate failed after design. No exception is requested.

## Project Structure

### Documentation (this feature)

```text
specs/003-verify-implementation/
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
│   ├── verification.py    # record a check; which changes lack a passing check
│   └── status.py          # complete also refuses changes that lack a passing check
├── storage/
│   ├── schema.sql         # implementation_check
│   └── verification_store.py
└── web/
    ├── api.py             # record-check command
    └── templates/detail.html

tests/
├── unit/test_verification.py
├── contract/test_verification_api.py
└── integration/test_replay.py   # same script twice, including these checks
```

**Structure Decision**: Extend `src/task_manager`. The new domain module does not import the web framework. Storage is the only writer of `implementation_check`. `status.py` asks the verification rules whether any carried-out change on that task lacks a passing check before it completes. It does not ask that question before cancel. The detail page and the JSON API call the same function. Tests are split so a rule can fail in `tests/unit` without a server, and a contract mismatch fails in `tests/contract`.

## Complexity Tracking

No constitution violations require justification.
