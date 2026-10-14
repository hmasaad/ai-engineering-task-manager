# Implementation Plan: Durable Workflow Orchestration

**Branch**: `020-durable-workflow` | **Date**: 2026-10-14 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/020-durable-workflow/spec.md`

## Summary

An In Progress task stores ordered workflow steps. Each step is Read a file or Create a folder. One advance performs the first step that is not Completed and stores Pending, Completed, Waiting, or Failed. Opening the workspace again shows those states, and the next advance continues there. A refusal or an approval wait stops the run and names the step. The task status is unchanged.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI, Uvicorn, Jinja2, pytest. SQLite through `sqlite3`. No new dependency.

**Storage**: The existing SQLite workspace file. One new table, `workflow_step`. No new column on `task`.

**Testing**: pytest. Unit tests cover stored steps, one advance, resume after reopen, a failed step, and a waiting step. Contract tests cover the commands. Existing feature tests stay green.

**Target Platform**: Local machine. The server binds to `127.0.0.1` only.

**Project Type**: Local web application with a domain library in the same process

**Performance Goals**: Advancing a workflow of 500 steps reads those steps once and performs one action. That read finishes in under 200 milliseconds before the action runs.

**Constraints**: One engineer, no sign-in. Constitution v1.0.0. Specifications 001 through 019 are not rewritten. `GET /api/tasks` stays the top-level task list. A failed step is returned as the task detail so the stored state is kept. A Refusal rolls the transaction back.

**Scale/Scope**: One engineer and one workspace file per start. One step added, removed, or advanced per request. Two actions: `read` and `folder`.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution: `.specify/memory/constitution.md` v1.0.0.

### Before research

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | The spec names the stored steps, one advance, resume, and the stop sentence. |
| II. Test-first verification | Pass | The spec says the rules are covered by automated checks. This phase produces no application code. |
| III. Explicit task state | Pass | Task statuses stay Draft, Ready, In Progress, Completed, and Cancelled. A step has its own stored state. |
| IV. Traceability | Pass | A step belongs to one task. A waiting step names the change it recorded. |
| V. Deterministic behavior | Pass | The next step is the first that is not Completed. Reopening does not perform a step. |
| VI. Observable AI actions | Pass | Each performed step keeps the record that action already writes. |
| VII. Human approval | Pass | A consequential folder waits. Approval does not advance the workflow. |
| VIII. Small, independently verifiable changes | Pass | Three stories. Other actions stay on their own commands. |

No gate failed.

### After design

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | [data-model.md](data-model.md) names `workflow_step` and the four step states. |
| II. Test-first verification | Pass | [quickstart.md](quickstart.md) names the tests that must pass. |
| III. Explicit task state | Pass | [research.md](research.md) leaves task status unchanged. |
| IV. Traceability | Pass | [contracts/commands.md](contracts/commands.md) stores one step on one task and keeps `change_id` for a folder step. |
| V. Deterministic behavior | Pass | Advance selects the lowest position that is not Completed. |
| VI. Observable AI actions | Pass | Read and folder keep their existing records. The step state is stored beside them. |
| VII. Human approval | Pass | Waiting does not call the action again. The existing approval command is unchanged. |
| VIII. Small, independently verifiable changes | Pass | One table and two existing actions. |

No gate failed after design. No exception is requested.

## Project Structure

### Documentation (this feature)

```text
specs/020-durable-workflow/
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
├── storage/workflow_store.py
├── storage/schema.sql
├── web/api.py
├── web/pages.py
└── web/templates/detail.html

tests/
├── unit/test_workflow.py
└── contract/test_workflow_api.py
```

**Structure Decision**: The step rules live in `domain/workflow.py` and call the existing read and folder commands. The table lives in `workflow_store.py`. Pages and the API call the same workspace methods.
