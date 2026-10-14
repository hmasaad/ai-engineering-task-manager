# Implementation Plan: Instruction Page

**Branch**: `023-instruction-page` | **Date**: 2026-10-14 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/023-instruction-page/spec.md`

## Summary

Instructions shows the saved model and one task instruction. Saving the model keeps the name and the text it returns. Starting work creates an In Progress task, reads one file, and asks that model once for the file to change. A refusal stores nothing.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI, Uvicorn, Jinja2, pytest. SQLite through `sqlite3`. No new dependency.

**Storage**: The existing SQLite workspace file. One new table, `configured_model`. No new column on `task`.

**Testing**: pytest. Unit tests cover a saved model, a new file, a waiting replacement, and a refusal that stores nothing. Contract tests cover the page. Existing feature tests stay green.

**Target Platform**: Local machine. The server binds to `127.0.0.1` only.

**Project Type**: Local web application with a domain library in the same process

**Performance Goals**: Opening Instructions is one read of the saved model. Starting work is the existing read plus one model call.

**Constraints**: One engineer, no sign-in. Constitution v1.0.0. Specifications 001 through 022 are not rewritten. `GET /api/tasks` stays the top-level task list. A Refusal still rolls its own transaction back, so a failed start leaves no task.

**Scale/Scope**: One engineer and one workspace file per start. One model save or one start per request.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution: `.specify/memory/constitution.md` v1.0.0.

### Before research

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | The spec names the saved model, the one start, and the refusal that stores nothing. |
| II. Test-first verification | Pass | The spec says the rules are covered by automated checks. This phase produces no application code. |
| III. Explicit task state | Pass | Starting work uses the existing Ready and In Progress transitions. |
| IV. Traceability | Pass | The task keeps the file read and the model result. |
| V. Deterministic behavior | Pass | The saved model returns its stored text. |
| VI. Observable AI actions | Pass | The model is asked once and the text is stored with the change. |
| VII. Human approval | Pass | A replacement waits. Starting work does not approve it. |
| VIII. Small, independently verifiable changes | Pass | One page, one model, and one file change. |

No gate failed.

### After design

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | [data-model.md](data-model.md) names `configured_model`. |
| II. Test-first verification | Pass | [quickstart.md](quickstart.md) names the tests that must pass. |
| III. Explicit task state | Pass | [research.md](research.md) starts the task through the existing transitions. |
| IV. Traceability | Pass | [contracts/commands.md](contracts/commands.md) returns the task detail. |
| V. Deterministic behavior | Pass | The same saved text is returned on the next start. |
| VI. Observable AI actions | Pass | One model call is stored on the change. |
| VII. Human approval | Pass | An existing file stays unchanged until approval. |
| VIII. Small, independently verifiable changes | Pass | One new table and one page. |

No gate failed after design. No exception is requested.

## Project Structure

### Documentation (this feature)

```text
specs/023-instruction-page/
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
├── domain/instruction.py
├── storage/model_config_store.py
├── storage/schema.sql
├── workspace.py
├── web/api.py
├── web/pages.py
├── web/templates/base.html
└── web/templates/instructions.html

tests/
├── unit/test_instruction_page.py
└── contract/test_instruction_page_api.py
```

**Structure Decision**: Saving the model and starting work live in `domain/instruction.py`. The page and the API call the same workspace methods. One transaction rolls back when start is refused.
