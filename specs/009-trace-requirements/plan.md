# Implementation Plan: Trace Requirements

**Branch**: `009-trace-requirements` | **Date**: 2026-10-12 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/009-trace-requirements/spec.md`

## Summary

An engineer records a functional or non-functional requirement in the one local workspace, links it to tasks and acceptance criteria, names the checks it needs, and records Passed or Failed with a run identifier. The product stores that record. It does not run the check. A linked criterion cannot become Verified, and a linked task cannot be completed, while a check that is still named is not currently Passed. A gap list shows requirements that are missing a task, a criterion, a named check, or a current pass. Changing the statement or the kind keeps the identifier, lists the trace, and returns linked Verified criteria to Unverified.

The work extends the existing Python process. New tables only. No new dependency, and no new task status.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI, Uvicorn, Jinja2, pytest. SQLite through `sqlite3`. No new dependency.

**Storage**: The same SQLite workspace file. New tables for the requirement, its task links, its criterion links, its named checks, and its verification runs. Existing tables are not altered. A named check is retired in place so its runs remain readable.

**Testing**: pytest. Unit tests cover one rule at a time. Contract tests cover the HTTP commands. One integration test walks a requirement through a task, a criterion, and a stored run. Existing completion and verification tests stay green for tasks with no linked requirement.

**Target Platform**: Local machine. The server binds to `127.0.0.1` only.

**Project Type**: Local web application with a domain library in the same process

**Performance Goals**: Opening the gap list, opening one requirement, and completing a task each finish in under 200 milliseconds on a workspace of 5,000 tasks and 5,000 requirements. Completion looks up requirements linked to that task. It does not scan every requirement.

**Constraints**: One workspace, no sign-in, and no execution of the named checks. The client cannot choose the engineer name or the time. A requirement identifier is assigned once and is not edited. Constitution v1.0.0. Specifications 001 through 008 are not rewritten.

**Scale/Scope**: One engineer and one workspace. This feature adds requirement records, links, named checks, and stored runs. It does not add a task status, a model call, or a file write.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution: `.specify/memory/constitution.md` v1.0.0.

### Before research

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | The spec names the engineer, the identifier, the kind, the links, the run, and pass/fail scenarios for every story. |
| II. Test-first verification | Pass | This phase produces no application code. |
| III. Explicit task state | Pass | Task status stays Draft, Ready, In Progress, Completed, or Cancelled. A requirement change that unverifies a criterion uses a stored history cause. |
| IV. Traceability | Pass | The feature stores the requirement, the task, the criterion, the named check, and the run. |
| V. Deterministic behavior | Pass | The product stores the result the engineer records. It does not run a check. An unchanged statement and kind does not change state. |
| VI. Observable AI actions | Pass | No assistant command is added. The engineer is the actor on every new record. |
| VII. Human approval | Pass | The engineer submits the requirement change. Runs stay. The effect matches the existing rule that editing a Verified criterion clears that verification. |
| VIII. Small, independently verifiable changes | Pass | One workspace feature. It does not run tests, create folders, or rewrite earlier specifications. |

No gate failed.

### After design

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | [data-model.md](data-model.md) and the contracts restate the guards, the gap list, and the unchanged save. |
| II. Test-first verification | Pass | [quickstart.md](quickstart.md) requires failing tests before the behavior is done, including one rule alone and the full path. |
| III. Explicit task state | Pass | [research.md](research.md) reuses the existing leave-completed path with cause `requirement_changed`. No status is added. |
| IV. Traceability | Pass | A requirement links to tasks and criteria. A run points at one named check. The task detail lists linked `REQ-` identifiers. |
| V. Deterministic behavior | Pass | The current result is the latest run by time, then by id. Replay reads stored rows and does not invent a pass. |
| VI. Observable AI actions | Pass | The API ignores a client-supplied engineer name and time. Removed checks keep their runs. |
| VII. Human approval | Pass | Clearing a Verified criterion happens only when the engineer changes the statement or the kind. An unchanged save writes nothing. |
| VIII. Small, independently verifiable changes | Pass | The requirement page and the API call the same domain functions. Tasks with no link keep today's completion sentence. |

No gate failed after design. No exception is requested.

## Project Structure

### Documentation (this feature)

```text
specs/009-trace-requirements/
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
├── domain/requirement.py
├── domain/capture.py            # criterion removal drops the link; verify consults named checks
├── domain/status.py             # completion sentence gains the required-check clause
├── storage/schema.sql
├── storage/requirement_store.py
├── storage/task_store.py        # task detail lists linked requirements
├── workspace.py
└── web/
    ├── api.py
    ├── pages.py
    └── templates/
        ├── requirements.html
        ├── requirement.html
        └── detail.html

tests/
├── unit/test_requirement.py
├── unit/test_requirement_run.py
├── unit/test_requirement_gaps.py
├── unit/test_requirement_change.py
├── contract/test_requirement_api.py
├── contract/test_requirement_run_api.py
└── integration/test_requirement_trace.py
```

**Structure Decision**: Extend `src/task_manager`. The domain module is the only writer of requirement rows. Pages and the API call that module. Storage does not decide whether a check blocks completion. Existing feature 003 checks stay on the implementation change and are not reused as runs.

## Complexity Tracking

No constitution violations require justification.
