---
description: "Task list for Idempotency and Duplicate Execution Control"
---

# Tasks: Idempotency and Duplicate Execution Control

**Input**: Design documents from `/specs/033-duplicate-execution/`

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

**Purpose**: The execution table. No existing table is altered.

- [X] T001 Add `command_execution` in `src/task_manager/storage/schema.sql` with `CREATE TABLE IF NOT EXISTS` only, as in `specs/033-duplicate-execution/data-model.md`. `UNIQUE (task_id, name)`. `action` is `read` or `folder`. `name` and `path` are trimmed and not empty.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: One execution can be stored and read for a task.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T002 Read and insert executions in `src/task_manager/storage/execution_store.py`. A second insert for the same task and name does not add a row. Add the lookup used by `src/task_manager/domain/execution.py`.

**Checkpoint**: An execution can be stored beside its task.

---

## Phase 3: User Story 1 - One name performs one command (Priority: P1) 🎯 MVP

**Goal**: The first accepted name reads a file or creates a folder once. The same name does not do it again.

**Independent Test**: Name a read "once". Remove the file and send "once" again. The file read stays the only one.

### Tests for User Story 1

- [X] T003 [P] [US1] Add the repeated read and folder checks in `tests/unit/test_duplicate_execution.py`. Confirm they fail before the behavior exists.

### Implementation for User Story 1

- [X] T004 [US1] Remember an accepted execution and return the earlier one in `src/task_manager/domain/file_read.py` and `src/task_manager/domain/folder.py`. Pass the optional name from `src/task_manager/workspace.py`.

**Checkpoint**: A repeated name leaves a removed file or folder removed.

---

## Phase 4: User Story 2 - A refusal does not use the name (Priority: P2)

**Goal**: A blank name, a refusal, and a rolled-back command leave the name free.

**Independent Test**: A missing file named "once" saves nothing. The same name reads the file once it exists.

### Tests for User Story 2

- [X] T005 [P] [US2] Extend `tests/unit/test_duplicate_execution.py` for a blank name, a missing file, a rolled-back read, another task, and a task that is not In Progress.

### Implementation for User Story 2

- [X] T006 [US2] Store the name only after the command is accepted in `src/task_manager/domain/execution.py`. A Refusal leaves no row.

**Checkpoint**: The same name can be used after a refusal.

---

## Phase 5: User Story 3 - The task shows the named executions (Priority: P3)

**Goal**: The page lists the executions and offers an execution name.

**Independent Test**: The page shows "once" for `note.txt`, and submitting that name again does not read the file again.

### Tests for User Story 3

- [X] T007 [P] [US3] Add `tests/contract/test_duplicate_execution_api.py` for the page, `POST /api/tasks/{id}/file-reads`, and `POST /api/tasks/{id}/folders`.

### Implementation for User Story 3

- [X] T008 [US3] Show Executions in `src/task_manager/web/templates/detail.html`. Accept `execution` in `src/task_manager/web/api.py` and `src/task_manager/web/pages.py`. Include `executions` from `src/task_manager/storage/task_store.py`.

**Checkpoint**: The page and the command agree on the named execution.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T009 Run the checks in `specs/033-duplicate-execution/quickstart.md` and confirm the existing suite stays green.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on T001. Blocks the stories.
- **User Story 1 (Phase 3)**: Depends on Phase 2.
- **User Story 2 (Phase 4)**: Depends on User Story 1, because a refusal is the path that does not store the name.
- **User Story 3 (Phase 5)**: Depends on User Story 1, because the page shows a stored execution.
- **Polish (Phase 6)**: Depends on the stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Independently testable by naming one read.
- **User Story 2 (P2)**: Independently testable once a name can be stored.
- **User Story 3 (P3)**: Independently testable once the execution is on the task.

### Parallel Opportunities

- T005 and T007 touch different test files and can be written together.

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete User Story 1.
3. Stop and validate one execution per name.

### Incremental Delivery

1. Store the name with the accepted command.
2. Leave the name free when the command is refused.
3. Show the execution on the task.

## Notes

- Do not record an execution for a workflow step.
- Do not change a named workflow advance.
- Commit only when the engineer asks.
