# Implementation Plan: Real Model

**Branch**: `024-real-model` | **Date**: 2026-10-14 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/024-real-model/spec.md`

## Summary

Instructions saves a model name, a service address, and an optional key. Starting work sends the task, what changed, and the file text to that service once. The reply is the file text. An existing file waits for approval. A fixed model text is no longer saved or sent.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI, Uvicorn, Jinja2, pytest. SQLite through `sqlite3`. HTTP through `urllib.request`. No new dependency.

**Storage**: The existing SQLite workspace file. One new table, `model_service`. `configured_model` is left in place and is no longer read.

**Testing**: pytest. A local service stands in for the model. Unit tests cover a revised file, an unreachable service, and an empty reply. Contract tests cover the page. Existing feature tests stay green.

**Target Platform**: Local machine. The server binds to `127.0.0.1` only. The model service is the address the engineer saved.

**Project Type**: Local web application with a domain library in the same process

**Performance Goals**: Saving the service is one write. One start makes one model request.

**Constraints**: One engineer, no sign-in. Constitution v1.0.0. Specifications 001 through 023 are not rewritten. `GET /api/tasks` stays the top-level task list. A Refusal still rolls its own transaction back. The key is not stored in the prompt. The request waits at most 120 seconds.

**Scale/Scope**: One engineer and one workspace file per start. One service save or one start per request.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution: `.specify/memory/constitution.md` v1.0.0.

### Before research

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | The spec names the service, the one request, and the reply that waits before replacing a file. |
| II. Test-first verification | Pass | The spec says the rules are covered by automated checks. This phase produces no application code. |
| III. Explicit task state | Pass | Starting work uses the existing Ready and In Progress transitions. |
| IV. Traceability | Pass | The reply is stored with the change. |
| V. Deterministic behavior | Pass | The reply is stored. Approval reads that stored reply. |
| VI. Observable AI actions | Pass | The prompt and the reply are stored. The service is asked once. |
| VII. Human approval | Pass | An existing file stays unchanged until the engineer approves. |
| VIII. Small, independently verifiable changes | Pass | One service and one file reply. |

No gate failed.

### After design

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | [data-model.md](data-model.md) names `model_service`. |
| II. Test-first verification | Pass | [quickstart.md](quickstart.md) names the tests that must pass. |
| III. Explicit task state | Pass | [research.md](research.md) leaves completion and approval on their existing commands. |
| IV. Traceability | Pass | [contracts/commands.md](contracts/commands.md) stores the reply on the change. |
| V. Deterministic behavior | Pass | Approval writes the stored reply and does not ask the service again. |
| VI. Observable AI actions | Pass | The request includes the file text and what changed. |
| VII. Human approval | Pass | A replacement stays Awaiting approval. |
| VIII. Small, independently verifiable changes | Pass | One new table and one request. |

No gate failed after design. No exception is requested.

## Project Structure

### Documentation (this feature)

```text
specs/024-real-model/
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
├── model.py
├── domain/instruction.py
├── domain/model_file.py
├── storage/model_config_store.py
├── storage/schema.sql
├── workspace.py
├── web/api.py
├── web/pages.py
└── web/templates/instructions.html

tests/
├── unit/test_instruction_page.py
└── contract/test_instruction_page_api.py
```

**Structure Decision**: The service call lives in `model.py`. Starting work still goes through the existing file read and model proposal. The key stays on the service row and out of the stored prompt.
