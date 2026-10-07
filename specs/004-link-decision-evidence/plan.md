# Implementation Plan: Link a Decision to Its Evidence

**Branch**: `004-link-decision-evidence` | **Date**: 2026-10-07 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/004-link-decision-evidence/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

An engineer records a decision that names exactly one change check on the same task. The task then shows that decision with the statement, the rationale, the time, the criterion wording stored on the check, the account of what changed, the evidence, and Passed or Failed. The decision stays on that check when a later check of the same change and criterion is recorded. The existing decision that has only a statement and a rationale remains. Completion and cancellation do not gain a new refusal.

The work stays in the existing Python 3.12 process. A new insert-only link table sits beside the decision rows from feature 001. The task detail page and the JSON API call one new domain function. The existing decision function is unchanged. Research is in [research.md](research.md).

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI, Uvicorn, Jinja2, pytest. SQLite through the standard-library `sqlite3` driver. No new dependency.

**Storage**: The same SQLite workspace file. One new insert-only table, `decision_check`, with at most one row per decision and no row when the decision names no check.

**Testing**: pytest. Domain tests call the rules directly. Contract tests call the HTTP commands with FastAPI's test client. The existing scripted clock supplies timestamps.

**Target Platform**: Local machine. The server binds to `127.0.0.1` only.

**Project Type**: Local web application with a domain library in the same process

**Performance Goals**: Recording a decision that names a check completes in under 200 milliseconds on a workspace of 5,000 tasks, 5,000 checks, and 5,000 decisions.

**Constraints**: No sign-in, no assistant actor, no file list, no test runner, no review link, no edit or delete of a saved decision. The client cannot choose the engineer name or the time. Naming a check does not verify a criterion, record a check, or change task status. A missing decision does not block completion or cancellation. Constitution v1.0.0.

**Scale/Scope**: One engineer and one workspace. The existing task detail page. This feature adds the named check on each linked decision and one record action beside the existing decision action.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution: `.specify/memory/constitution.md` v1.0.0.

### Before research

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | The spec names the engineer, the statement, the rationale, the one check, and pass/fail scenarios for every story. |
| II. Test-first verification | Pass | This phase produces no application code. Implementation is not started until tests exist for the scenario they prove. |
| III. Explicit task state | Pass | Task status stays the five stored statuses. A linked decision is a stored row, not an inferred state. |
| IV. Traceability | Pass | The decision names one check. That check already names the change, the criterion wording, the evidence, and the result, and the change names the task. |
| V. Deterministic behavior | Pass | The same commands must yield the same statements, named checks, and order. The existing clock remains the only time source. |
| VI. Observable AI actions | Pass | This feature has no assistant command. There is no agent action to hide. |
| VII. Human approval | Pass | The engineer writes the statement and the rationale and names the check in an explicit command. A Passed check is not a decision. |
| VIII. Small, independently verifiable changes | Pass | The three stories can be tested on their own. The plan does not add accounts, sharing, a completion gate, or an assistant. |

No gate failed. Research records how this feature uses the existing process. It does not relax a rule.

### After design

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | [data-model.md](data-model.md) and the contracts restate the spec guards, including the separate unlinked command and the rule that a later check does not move the decision. They do not add a behavior the spec does not name. |
| II. Test-first verification | Pass | [quickstart.md](quickstart.md) requires failing tests mapped to spec scenarios before a behavior is done. |
| III. Explicit task state | Pass | Task status is unchanged by recording the decision. The link is a stored row. `check` is null when the decision names none. |
| IV. Traceability | Pass | `decision_check` points at one `implementation_check`. Reading the decision joins that check and its change, so the criterion wording, the account of what changed, the evidence, and the result stay the ones stored on that check. |
| V. Deterministic behavior | Pass | [research.md](research.md) reuses the injected clock and lists decisions by `recorded_at`, then `id`. |
| VI. Observable AI actions | Pass | The API ignores a client-supplied engineer name and exposes no assistant route. |
| VII. Human approval | Pass | The linked command is its own HTTP action. A refused command commits nothing. There is no delete. Completion and cancellation are unchanged. |
| VIII. Small, independently verifiable changes | Pass | One process. The detail page calls the same function as the API. Stories map to separate quickstart scenarios. |

No gate failed after design. No exception is requested.

## Project Structure

### Documentation (this feature)

```text
specs/004-link-decision-evidence/
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
│   └── decisions.py       # add a decision that names one check; existing add stays
├── storage/
│   ├── schema.sql         # decision_check
│   ├── decision_store.py  # insert the link
│   └── task_store.py      # each decision includes the named check, or null
└── web/
    ├── api.py             # linked-decision command
    ├── pages.py           # same command from the detail page
    └── templates/detail.html

tests/
├── unit/test_linked_decision.py
├── contract/test_linked_decision_api.py
└── integration/test_replay.py   # same script twice, including this decision
```

**Structure Decision**: Extend `src/task_manager`. The new function lives in the existing decision module and does not import the web framework. Storage is the only writer of `decision_check`. `add_decision` does not gain a check argument. The detail page and the JSON API call the same new function. Tests are split so a rule can fail in `tests/unit` without a server, and a contract mismatch fails in `tests/contract`.

## Complexity Tracking

No constitution violations require justification.
