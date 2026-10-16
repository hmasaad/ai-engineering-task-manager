---
description: "Task list for Workflow Observability and Distributed Tracing"
---

# Tasks: Workflow Observability and Distributed Tracing

**Input**: Design documents from `/specs/030-workflow-tracing/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Included. The spec says the rules are covered by automated checks. Constitution Principle II requires a failing test before the behavior exists.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested on its own.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Single project: `src/task_manager/`, `tests/` at the repository root

## Phase 1: Setup

**Purpose**: The trace tables. No existing table is altered.

- [X] T001 Add `workflow_trace` and `workflow_span` in `src/task_manager/storage/schema.sql` with `CREATE TABLE IF NOT EXISTS` only, as in `specs/030-workflow-tracing/data-model.md`. `workflow_trace.task_id` is unique. A span state is `Running`, `Completed`, `Failed`, or `Waiting`. `ended_at` is null while the span is open.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: A trace and its spans can be stored and read for one task.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T002 Read and insert a trace and its spans in `src/task_manager/storage/workflow_store.py`. One task has one trace. An open span is the span for a step whose `ended_at` is null.

**Checkpoint**: A span can be stored beside its step.

---

## Phase 3: User Story 1 - A workflow run keeps one trace (Priority: P1) 🎯 MVP

**Goal**: Starting a step opens a span, and finishing the step closes it on the same trace.

**Independent Test**: Advance two reads. Both spans share one trace, and the second follows the first.

### Tests for User Story 1

- [X] T003 [P] [US1] Add the trace checks in `tests/unit/test_workflow_tracing.py`. Confirm they fail before the behavior exists.

### Implementation for User Story 1

- [X] T004 [US1] Open a span when a step starts and close it when the step is Completed, Failed, or Waiting in `src/task_manager/domain/workflow.py`. Report `trace` from the task detail.

**Checkpoint**: A rolled-back start leaves no trace.

---

## Phase 4: User Story 2 - Reading the trace does not run the workflow (Priority: P2)

**Goal**: A trace read returns the stored spans and does not move the clock.

**Independent Test**: Read the trace twice. The spans match and the clock is unchanged.

### Tests for User Story 2

- [X] T005 [P] [US2] Extend `tests/unit/test_workflow_tracing.py` for a repeated read, an unknown task, and the clock.

### Implementation for User Story 2

- [X] T006 [US2] Add a read-only trace command in `src/task_manager/domain/workflow.py` and `src/task_manager/workspace.py`. Use `Task not found.` from `specs/030-workflow-tracing/contracts/commands.md`.

**Checkpoint**: Reading the trace does not start a step.

---

## Phase 5: User Story 3 - The task shows the trace (Priority: P3)

**Goal**: The page shows the trace and the span it follows.

**Independent Test**: The page says `No trace yet.` before the workflow runs, then shows the completed span.

### Tests for User Story 3

- [X] T007 [P] [US3] Add `tests/contract/test_workflow_tracing_api.py` for the page and `GET /api/tasks/{id}/workflow/trace`.

### Implementation for User Story 3

- [X] T008 [US3] Show the trace in `src/task_manager/web/templates/detail.html` and accept the read in `src/task_manager/web/api.py`.

**Checkpoint**: The page and the command agree on the trace.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T009 Run the checks in `specs/030-workflow-tracing/quickstart.md` and confirm the existing suite stays green.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on T001. Blocks the stories.
- **User Story 1 (Phase 3)**: Depends on Phase 2.
- **User Story 2 (Phase 4)**: Depends on User Story 1, because the read returns spans that the advance stored.
- **User Story 3 (Phase 5)**: Depends on User Story 2, because the page shows the same trace the command returns.
- **Polish (Phase 6)**: Depends on the stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Independently testable by advancing two reads.
- **User Story 2 (P2)**: Independently testable once a span is stored.
- **User Story 3 (P3)**: Independently testable once the trace is reported.

### Parallel Opportunities

- T005 and T007 touch different test files and can be written together.

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete User Story 1.
3. Stop and validate one trace for two steps.

### Incremental Delivery

1. Open and close a span with the step.
2. Read that trace without running the workflow.
3. Show the trace on the task.

## Notes

- Do not add a span for a delivery, a rejection, or a compensation.
- Do not call the clock while reading the trace.
- Commit only when the engineer asks.
