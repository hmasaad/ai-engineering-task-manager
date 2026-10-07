# Implementation Plan: Assist an Ordinary Change

**Branch**: `005-assist-ordinary-change` | **Date**: 2026-10-07 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/005-assist-ordinary-change/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

An engineer asks the assistant to carry out one change for an In Progress task in a named project. The request includes the account of what the assistant changed or proposed. An ordinary request is stored as Carried out and names the assistant and the project. A consequential request, or an ordinary request that the assistant stopped because the work would be consequential, is stored as Awaiting approval and is not carried out. The engineer approves or declines that waiting change later. The assistant cannot approve or decline it. The command does not verify a criterion, record a check, record a decision, or change task status.

The work stays in the existing Python 3.12 process. The account in the request is the recorded output of the assistant. The command stores that account and does not call the assistant again. A new insert-only table sits beside the implementation change from feature 002. Research is in [research.md](research.md).

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI, Uvicorn, Jinja2, pytest. SQLite through the standard-library `sqlite3` driver. No new dependency.

**Storage**: The same SQLite workspace file. One new insert-only table, `assistant_change`, with at most one row per implementation change. One new one-row table, `workspace_assistant`, for the configured assistant name.

**Testing**: pytest. Domain tests call the rules directly. Contract tests call the HTTP commands with FastAPI's test client. The existing scripted clock supplies timestamps.

**Target Platform**: Local machine. The server binds to `127.0.0.1` only.

**Project Type**: Local web application with a domain library in the same process

**Performance Goals**: Recording an assistant change completes in under 200 milliseconds on a workspace of 5,000 tasks and 5,000 implementation changes.

**Constraints**: No sign-in, no model call, no write into the named project, no file list, no test runner, no review link. The client cannot choose the assistant name, the engineer name, or the time. An assistant change does not verify a criterion, record a check, record a decision, or change task status. A consequential change is not stored as Carried out. Constitution v1.0.0.

**Scale/Scope**: One engineer, one assistant name, and one workspace. The existing task detail page. This feature adds one assistant-change action beside the engineer's record-change action.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution: `.specify/memory/constitution.md` v1.0.0.

### Before research

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | The spec names the engineer, the assistant, the project, ordinary and consequential, and pass/fail scenarios for every story. |
| II. Test-first verification | Pass | This phase produces no application code. Implementation is not started until tests exist for the scenario they prove. |
| III. Explicit task state | Pass | Task status stays the five stored statuses. The change outcome stays Carried out, Awaiting approval, or Not carried out. |
| IV. Traceability | Pass | The change names one task, one project, and the account of what changed. The existing check can name that change. |
| V. Deterministic behavior | Pass | The same stored account, project, class, and clock must yield the same outcome. The assistant's wording is part of the stored request. |
| VI. Observable AI actions | Pass | The stored change is the assistant's record: the task, the project, the account, the assistant, and the outcome. |
| VII. Human approval | Pass | A consequential change is not carried out. The engineer approves or declines it in a later action. The assistant cannot approve it. |
| VIII. Small, independently verifiable changes | Pass | The three stories can be tested on their own. The plan does not add a model, a project editor, accounts, or sharing. |

No gate failed. Research records how this feature uses the existing process. It does not relax a rule.

### After design

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | [data-model.md](data-model.md) and the contracts restate the spec guards, including the stop that stores Awaiting approval and the refusal of an assistant approval. They do not add a behavior the spec does not name. |
| II. Test-first verification | Pass | [quickstart.md](quickstart.md) requires failing tests mapped to spec scenarios before a behavior is done. |
| III. Explicit task state | Pass | Task status is unchanged. Ordinary with no stop is Carried out. Consequential, and an ordinary request that stopped, are Awaiting approval through the existing outcome rule. |
| IV. Traceability | Pass | `assistant_change` points at one `implementation_change`, which already points at the task. The row stores the project and the assistant name. |
| V. Deterministic behavior | Pass | [research.md](research.md) treats the account in the request as the recorded assistant output. Replay runs the same command script. It does not call an assistant. |
| VI. Observable AI actions | Pass | The API ignores a client-supplied assistant name. The stored row keeps the configured name, the project, the account, and the outcome. |
| VII. Human approval | Pass | Approve and decline stay the engineer's commands. `actor` of `assistant` on those commands is refused and writes nothing. |
| VIII. Small, independently verifiable changes | Pass | One process. The detail page calls the same function as the API. The command does not open the named project. |

No gate failed after design. No exception is requested.

## Project Structure

### Documentation (this feature)

```text
specs/005-assist-ordinary-change/
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
│   └── implementation.py  # record an assistant change; existing record stays
├── storage/
│   ├── schema.sql         # assistant_change, workspace_assistant
│   ├── implementation_store.py
│   └── connection.py      # save the configured assistant name
└── web/
    ├── api.py             # assistant-change command; refuse assistant approval
    ├── pages.py
    └── templates/detail.html

tests/
├── unit/test_assistant_change.py
├── contract/test_assistant_change_api.py
└── integration/test_replay.py   # same script twice, including this record
```

**Structure Decision**: Extend `src/task_manager`. The new function lives in the existing implementation module and does not import the web framework. Storage is the only writer of `assistant_change`. `record` does not gain a project or an assistant argument. The detail page and the JSON API call the same new function. Tests are split so a rule can fail in `tests/unit` without a server, and a contract mismatch fails in `tests/contract`.

## Complexity Tracking

No constitution violations require justification.
