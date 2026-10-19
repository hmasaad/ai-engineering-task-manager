---
description: "Task list for Run One File Read"
---

# Tasks: Run One File Read

**Input**: Design documents from `/specs/036-run-file-read/`

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

**Purpose**: The run table. No existing table is altered.

- [X] T001 Add `workflow_file_run` in `src/task_manager/storage/schema.sql` with `CREATE TABLE IF NOT EXISTS` only, as in `specs/036-run-file-read/data-model.md`. `UNIQUE (task_id, name)`. `name` is trimmed and not empty. `step_id` is required and is not unique.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: One run can be stored and read for a file-read step.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T002 Read and insert runs in `src/task_manager/storage/workflow_store.py`. A second insert for the same task and name does not add a row. Return runs oldest first with the step title.

**Checkpoint**: A run can be stored beside its step.

---

## Phase 3: User Story 1 - Run the next file read (Priority: P1) 🎯 MVP

**Goal**: One named run reads the next file and leaves every later step pending.

**Independent Test**: Run "once". Only the first file is read. Run "next". Only the second file is read.

### Tests for User Story 1

- [X] T003 [P] [US1] Add the one-read and second-read checks in `tests/unit/test_run_file_read.py`. Confirm they fail before the behavior exists.

### Implementation for User Story 1

- [X] T004 [US1] Perform the next file-read step in `src/task_manager/domain/workflow.py`. Pass the command through `src/task_manager/workspace.py`. Use the existing prepare and finish path with no advance name, in the same transaction as the run name. Do not perform a later step.

**Checkpoint**: A second name reads only the next file.

---

## Phase 4: User Story 2 - A run that does not finish leaves the step pending (Priority: P2)

**Goal**: A refusal or a rolled-back run leaves the step pending.

**Independent Test**: Roll back "once". The step stays pending and the file has no stored read.

### Tests for User Story 2

- [X] T005 [P] [US2] Extend `tests/unit/test_run_file_read.py` for a blank name, no file, a folder step, a rolled-back run, a missing file, another task, and a task that is not In Progress.

### Implementation for User Story 2

- [X] T006 [US2] Store the run only after the file-read step is performed in `src/task_manager/domain/workflow.py`. Use the sentences in `specs/036-run-file-read/contracts/commands.md`. A Refusal leaves no row. A missing file fails that step and stores the name.

**Checkpoint**: A rolled-back run leaves the step pending.

---

## Phase 5: User Story 3 - The task shows the run (Priority: P3)

**Goal**: The page shows the run and Run file read.

**Independent Test**: The page offers Run file read, and after "once" the following folder step stays pending.

### Tests for User Story 3

- [X] T007 [P] [US3] Add `tests/contract/test_run_file_read_api.py` for the page and `POST /api/tasks/{id}/workflow/runs`.

### Implementation for User Story 3

- [X] T008 [US3] Show File reads run in `src/task_manager/web/templates/detail.html`. Accept the command in `src/task_manager/web/api.py` and `src/task_manager/web/pages.py`. Include `runs` and `can_run_read` from `src/task_manager/domain/workflow.py`.

**Checkpoint**: The page and the command agree on the run.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T009 Run the checks in `specs/036-run-file-read/quickstart.md` and confirm the existing suite stays green.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on T001. Blocks the stories.
- **User Story 1 (Phase 3)**: Depends on Phase 2.
- **User Story 2 (Phase 4)**: Depends on User Story 1, because a rollback needs a run that can be stored.
- **User Story 3 (Phase 5)**: Depends on User Story 1, because the page shows a stored run.
- **Polish (Phase 6)**: Depends on the stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Independently testable by running one file read.
- **User Story 2 (P2)**: Independently testable once a run can be stored.
- **User Story 3 (P3)**: Independently testable once the run is on the task.

### Parallel Opportunities

- T005 and T007 touch different test files and can be written together.

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete User Story 1.
3. Stop and validate one named file read.

### Incremental Delivery

1. Read the next file.
2. Leave a rolled-back run pending.
3. Show the run on the task.

## Notes

- Do not write `workflow_advance` for a run name.
- Do not perform a folder, an approval, a delivery, a commit, or a pull request.
- Do not leave the step Running when the run rolls back.
- Commit only when the engineer asks.
