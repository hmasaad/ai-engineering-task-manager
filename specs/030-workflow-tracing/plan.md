# Implementation Plan: Workflow Observability and Distributed Tracing

**Branch**: `030-workflow-tracing` | **Date**: 2026-10-16 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/030-workflow-tracing/spec.md`

## Summary

The first running step opens one trace for the task and one span. Later steps add spans on that same trace and follow the first span. The span closes in the same result that completes, fails, or waits the step.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI, Uvicorn, Jinja2, pytest. SQLite through `sqlite3`. No new dependency.

**Storage**: The existing SQLite workspace file. Two new tables, `workflow_trace` and `workflow_span`. No column is added to an existing table.

**Testing**: pytest. Unit tests cover one trace for two steps, a failed span, a running span, a rolled-back start, and a read that does not move the clock. A contract test covers the page. Existing feature tests stay green.

**Target Platform**: Local machine. The server binds to `127.0.0.1` only.

**Project Type**: Local web application with a domain library in the same process

**Performance Goals**: One running step opens one span. One finished step closes that span. Reading the trace writes nothing.

**Constraints**: One engineer, no sign-in. Constitution v1.0.0. Specifications 001 through 029 are not rewritten. `GET /api/tasks` stays the top-level task list. A Refusal rolls its own transaction back. The trace read does not call the clock.

**Scale/Scope**: One engineer and one workspace file. One trace per task.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution: `.specify/memory/constitution.md` v1.0.0.

### Before research

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | The spec names the trace, the span, and `No trace yet.` |
| II. Test-first verification | Pass | The spec says the rules are covered by automated checks. This phase produces no application code. |
| III. Explicit task state | Pass | A span is Running, Completed, Failed, or Waiting. |
| IV. Traceability | Pass | Each span names the step and the span it follows. |
| V. Deterministic behavior | Pass | The start and end times are the times already recorded for the step. |
| VI. Observable AI actions | Pass | The span is the inspectable record of the step. |
| VII. Human approval | Pass | The trace records work. It does not delete or approve anything. |
| VIII. Small, independently verifiable changes | Pass | Two new tables for the workflow steps. |

No gate failed.

### After design

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | [data-model.md](data-model.md) names the trace and the span. |
| II. Test-first verification | Pass | [quickstart.md](quickstart.md) names the tests that must pass. |
| III. Explicit task state | Pass | [research.md](research.md) closes the span with the step. |
| IV. Traceability | Pass | [contracts/commands.md](contracts/commands.md) returns the parent span. |
| V. Deterministic behavior | Pass | A second read returns the same spans and does not call the clock. |
| VI. Observable AI actions | Pass | A rolled-back start leaves no span. |
| VII. Human approval | Pass | Reading the trace performs no consequential action. |
| VIII. Small, independently verifiable changes | Pass | Delivery and compensation do not gain spans. |

No gate failed after design. No exception is requested.

## Project Structure

### Documentation (this feature)

```text
specs/030-workflow-tracing/
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
└── web/templates/detail.html

tests/
├── unit/test_workflow_tracing.py
└── contract/test_workflow_tracing_api.py
```

**Structure Decision**: The span is stored beside the step and closed by the same result that records the step outcome.
