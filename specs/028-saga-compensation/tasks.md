---
description: "Task list for Saga Pattern and Compensation"
---

# Tasks: Saga Pattern and Compensation

**Input**: Design documents from `/specs/028-saga-compensation/`

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

**Purpose**: The compensation table. No existing table is altered.

- [X] T001 Add `workflow_compensation` in `src/task_manager/storage/schema.sql` with `CREATE TABLE IF NOT EXISTS` only, as in `specs/028-saga-compensation/data-model.md`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: One compensation can be stored and read for a step.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T002 Read and insert compensations in `src/task_manager/storage/workflow_store.py`. A second insert for the same step does not add a row.

**Checkpoint**: A compensation can be stored beside its step.

---

## Phase 3: User Story 1 - A failed workflow can be compensated in reverse (Priority: P1) 🎯 MVP

**Goal**: The latest completed read is compensated first, and the stored read remains.

**Independent Test**: Fail a workflow after two reads. The first compensation names the later read. The earlier read is next.

### Tests for User Story 1

- [X] T003 [P] [US1] Add the reverse-order checks in `tests/unit/test_saga_compensation.py`. Confirm they fail before the behavior exists.

### Implementation for User Story 1

- [X] T004 [US1] Add `compensate` in `src/task_manager/domain/workflow.py` and report `saga` from the task detail. Use the sentences in `specs/028-saga-compensation/contracts/commands.md`.

**Checkpoint**: A workflow that has not failed cannot be compensated.

---

## Phase 4: User Story 2 - Removing a folder waits for approval (Priority: P2)

**Goal**: A folder compensation waits, and approval removes only an empty folder.

**Independent Test**: Create a folder, fail the next step, compensate, and approve. The empty folder is removed. A folder that contains a file stays.

### Tests for User Story 2

- [X] T005 [P] [US2] Extend `tests/unit/test_saga_compensation.py` for a waiting folder, approval, a folder that contains a file, and a decline.

### Implementation for User Story 2

- [X] T006 [US2] Approve and decline a waiting compensation in `src/task_manager/domain/workflow.py`. Remove an empty folder only in the approval.

**Checkpoint**: A waiting compensation blocks the next step.

---

## Phase 5: User Story 3 - The task shows the saga (Priority: P3)

**Goal**: The page shows the saga and the compensation forms.

**Independent Test**: The page shows Saga Failed and Compensate, then the compensated step.

### Tests for User Story 3

- [X] T007 [P] [US3] Add `tests/contract/test_saga_compensation_api.py` for the page and `POST /api/tasks/{id}/workflow/compensate`.

### Implementation for User Story 3

- [X] T008 [US3] Show the saga in `src/task_manager/web/templates/detail.html` and accept the commands in `src/task_manager/web/api.py` and `src/task_manager/web/pages.py`.

**Checkpoint**: The page and the command agree on the saga.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T009 Run the checks in `specs/028-saga-compensation/quickstart.md` and confirm the existing suite stays green.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on T001. Blocks the stories.
- **User Story 1 (Phase 3)**: Depends on Phase 2.
- **User Story 2 (Phase 4)**: Depends on User Story 1, because a folder compensation uses the same reverse order.
- **User Story 3 (Phase 5)**: Depends on User Story 2, because the page can show a waiting compensation.
- **Polish (Phase 6)**: Depends on the stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Independently testable by compensating a failed read.
- **User Story 2 (P2)**: Independently testable once a folder step can be selected.
- **User Story 3 (P3)**: Independently testable once the saga is reported.

### Parallel Opportunities

- T005 and T007 touch different test files and can be written together.

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete User Story 1.
3. Stop and validate reverse order.

### Incremental Delivery

1. Compensate the latest completed read.
2. Wait before removing a folder.
3. Show the saga on the task.

## Notes

- Do not delete a stored file read.
- Do not remove a folder before approval.
- Commit only when the engineer asks.
