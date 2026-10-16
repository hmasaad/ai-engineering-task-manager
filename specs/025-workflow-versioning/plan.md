# Implementation Plan: Workflow Versioning and Migration

**Branch**: `025-workflow-versioning` | **Date**: 2026-10-16 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/025-workflow-versioning/spec.md`

## Summary

A task workflow has a current version. After it has run, the engineer revises the remaining work into one draft and migrates onto that draft with a reason. Steps that already ran stay stored and are not performed again. Pending steps left behind stay stored and are not performed.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI, Uvicorn, Jinja2, pytest. SQLite through `sqlite3`. No new dependency.

**Storage**: The existing SQLite workspace file. New tables `workflow_version`, `workflow_version_step`, and `workflow_migration`. No column is added to an existing table.

**Testing**: pytest. Unit tests cover version 1, a draft, and one migration. Contract tests cover the page and the commands. Existing feature tests stay green.

**Target Platform**: Local machine. The server binds to `127.0.0.1` only.

**Project Type**: Local web application with a domain library in the same process

**Performance Goals**: Revise and migrate are one write each. Advance still performs one step of the current version.

**Constraints**: One engineer, no sign-in. Constitution v1.0.0. Specifications 001 through 024 are not rewritten. `GET /api/tasks` stays the top-level task list. A Refusal still rolls its own transaction back. Reading the task does not write a version.

**Scale/Scope**: One engineer and one workspace file. One revise or one migration per request.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution: `.specify/memory/constitution.md` v1.0.0.

### Before research

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | The spec names version 1, the draft, and the migration reason. |
| II. Test-first verification | Pass | The spec says the rules are covered by automated checks. This phase produces no application code. |
| III. Explicit task state | Pass | Migration does not change the task status. Versions are current, draft, or superseded. |
| IV. Traceability | Pass | The migration stores the reason and both versions. |
| V. Deterministic behavior | Pass | The same current version and draft produce the same next version. |
| VI. Observable AI actions | Pass | Advance still records the step. Migration does not rewrite the replay. |
| VII. Human approval | Pass | Migration waits for a reason the engineer types. A waiting step is not approved by migration. |
| VIII. Small, independently verifiable changes | Pass | One version and one migration. |

No gate failed.

### After design

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | [data-model.md](data-model.md) names the version and the migration. |
| II. Test-first verification | Pass | [quickstart.md](quickstart.md) names the tests that must pass. |
| III. Explicit task state | Pass | [research.md](research.md) leaves task status unchanged. |
| IV. Traceability | Pass | [contracts/commands.md](contracts/commands.md) stores the reason with both versions. |
| V. Deterministic behavior | Pass | Advance reads the current version only. |
| VI. Observable AI actions | Pass | The replay is not rewritten. |
| VII. Human approval | Pass | A blank reason is refused. |
| VIII. Small, independently verifiable changes | Pass | Three new tables. |

No gate failed after design. No exception is requested.

## Project Structure

### Documentation (this feature)

```text
specs/025-workflow-versioning/
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
├── unit/test_workflow_versioning.py
└── contract/test_workflow_versioning_api.py
```

**Structure Decision**: Versions are new rows beside the existing steps. A step that already ran is the same row on the next version, so exactly-once behavior stays on that row.
