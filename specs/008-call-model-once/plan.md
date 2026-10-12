# Implementation Plan: Call the Model Once

**Branch**: `008-call-model-once` | **Date**: 2026-10-12 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/008-call-model-once/spec.md`

## Summary

An engineer asks the configured model for the text of one file on an In Progress task. The call input is the task and one stored file read. The returned text is written or proposed with the existing ordinary-file rules. The model name, the input, and the returned text are stored. Replay reads that record and does not call the model again.

The model is a small boundary in the existing Python process. Tests and the local app pass a scripted model that returns fixed text. No network client and no new dependency are added.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI, Uvicorn, Jinja2, pytest. SQLite through `sqlite3`. No new dependency.

**Storage**: The same SQLite workspace file. One new insert-only table, `model_call`, with one row per model file change.

**Testing**: pytest. A scripted model records each prompt and returns fixed text. The suite must show one call on success and no call on an earlier refusal.

**Target Platform**: Local machine. The server binds to `127.0.0.1` only.

**Project Type**: Local web application with a domain library in the same process

**Performance Goals**: One model file completes in under 200 milliseconds on a workspace of 5,000 tasks and 5,000 implementation changes, not counting time spent inside the model. The command reads at most the one existing file needed by the ordinary-file check and does not scan the project.

**Constraints**: No sign-in, no second model call, no new folder, and no write outside the project. The client cannot choose the model name, the assistant name, the engineer name, or the time. Constitution v1.0.0.

**Scale/Scope**: One engineer, one assistant, one configured model, and one workspace. This feature adds one command. Assistant changes that do not use it call no model.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution: `.specify/memory/constitution.md` v1.0.0.

### Before research

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | The spec names the engineer, the model, the stored read, the file, and pass/fail scenarios for every story. |
| II. Test-first verification | Pass | This phase produces no application code. |
| III. Explicit task state | Pass | Task status stays unchanged. The file outcome stays the existing three outcomes. |
| IV. Traceability | Pass | The call names one task, one file read, one file, and the model. |
| V. Deterministic behavior | Pass | The model call is the non-deterministic boundary. Replay uses the stored output. |
| VI. Observable AI actions | Pass | The stored row has the model name, the input, and the returned text. |
| VII. Human approval | Pass | A replacement, a consequential request, and a stopped request do not write until the engineer approves. |
| VIII. Small, independently verifiable changes | Pass | One model call and one file. No vendor client, no folder creation, and no completion change. |

No gate failed.

### After design

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | [data-model.md](data-model.md) and the contracts restate the guards and the single call. |
| II. Test-first verification | Pass | [quickstart.md](quickstart.md) requires failing tests before the behavior is done. |
| III. Explicit task state | Pass | A model file uses the existing change outcomes. |
| IV. Traceability | Pass | `model_call` points at one implementation change and one file read. |
| V. Deterministic behavior | Pass | [research.md](research.md) stores the prompt and the returned text. Opening the task does not call the model. |
| VI. Observable AI actions | Pass | The API ignores a client-supplied model name. The stored row keeps the configured model name and the returned text. |
| VII. Human approval | Pass | Approval writes the stored text and does not call the model. The assistant still cannot approve. |
| VIII. Small, independently verifiable changes | Pass | The detail page calls the same function as the API. Older assistant changes call no model. |

No gate failed after design. No exception is requested.

## Project Structure

### Documentation (this feature)

```text
specs/008-call-model-once/
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
├── model.py                 # scripted model boundary
├── domain/model_file.py     # one call, then the existing file command
├── storage/schema.sql       # model_call
├── storage/model_store.py
├── storage/implementation_store.py
├── workspace.py
└── web/
    ├── api.py
    ├── pages.py
    └── templates/detail.html

tests/
├── unit/test_model_file.py
├── contract/test_model_file_api.py
└── integration/test_replay.py
```

**Structure Decision**: Extend `src/task_manager`. The model is called from the domain, not from the page. Storage is the only writer of `model_call`. The existing file command still accepts text the engineer submits and does not call the model.

## Complexity Tracking

No constitution violations require justification.
