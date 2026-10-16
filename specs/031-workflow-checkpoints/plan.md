# Implementation Plan: Workflow Snapshots and Checkpointing

**Branch**: `031-workflow-checkpoints` | **Date**: 2026-10-16 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/031-workflow-checkpoints/spec.md`

## Summary

The engineer names a checkpoint and the task stores the current step states. The same name does not replace that snapshot. Restore puts a failed step with no stored effect back to Pending and leaves a completed step completed.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI, Uvicorn, Jinja2, pytest. SQLite through `sqlite3`. No new dependency.

**Storage**: The existing SQLite workspace file. Two new tables, `workflow_checkpoint` and `workflow_checkpoint_step`. No column is added to an existing table.

**Testing**: pytest. Unit tests cover an immutable snapshot, a restore after a failure, a stored effect, and a rolled-back checkpoint. A contract test covers the page. Existing feature tests stay green.

**Target Platform**: Local machine. The server binds to `127.0.0.1` only.

**Project Type**: Local web application with a domain library in the same process

**Performance Goals**: One request stores one checkpoint or restores one checkpoint.

**Constraints**: One engineer, no sign-in. Constitution v1.0.0. Specifications 001 through 030 are not rewritten. `GET /api/tasks` stays the top-level task list. A Refusal rolls its own transaction back. Restore does not delete a stored file read.

**Scale/Scope**: One engineer and one workspace file. One checkpoint or one restore per request.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution: `.specify/memory/constitution.md` v1.0.0.

### Before research

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | The spec names the snapshot and the restore sentences. |
| II. Test-first verification | Pass | The spec says the rules are covered by automated checks. This phase produces no application code. |
| III. Explicit task state | Pass | A checkpoint stores each step state. |
| IV. Traceability | Pass | The checkpoint name identifies the saved point. |
| V. Deterministic behavior | Pass | The same name returns the original snapshot. |
| VI. Observable AI actions | Pass | Restore does not run a step. |
| VII. Human approval | Pass | A stored effect is not overwritten. |
| VIII. Small, independently verifiable changes | Pass | Two new tables. |

No gate failed.

### After design

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | [data-model.md](data-model.md) names the checkpoint and its steps. |
| II. Test-first verification | Pass | [quickstart.md](quickstart.md) names the tests that must pass. |
| III. Explicit task state | Pass | [research.md](research.md) restores only a failed step with no stored effect. |
| IV. Traceability | Pass | [contracts/commands.md](contracts/commands.md) keeps the snapshot with the name. |
| V. Deterministic behavior | Pass | A repeated name does not write a second snapshot. |
| VI. Observable AI actions | Pass | File reads and spans stay in place. |
| VII. Human approval | Pass | Restore refuses a step that already stored an effect. |
| VIII. Small, independently verifiable changes | Pass | One checkpoint per request. |

No gate failed after design. No exception is requested.

## Project Structure

### Documentation (this feature)

```text
specs/031-workflow-checkpoints/
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
├── workspace.py
├── web/api.py
├── web/pages.py
└── web/templates/detail.html

tests/
├── unit/test_workflow_checkpoints.py
└── contract/test_workflow_checkpoints_api.py
```

**Structure Decision**: The snapshot is stored beside the workflow. Restore changes only the state of a failed step that has no stored effect.
