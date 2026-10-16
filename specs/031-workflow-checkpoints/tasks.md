---
description: "Task list for Workflow Snapshots and Checkpointing"
---

# Tasks: Workflow Snapshots and Checkpointing

**Input**: Design documents from `/specs/031-workflow-checkpoints/`

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

**Purpose**: The checkpoint tables. No existing table is altered.

- [X] T001 Add `workflow_checkpoint` and `workflow_checkpoint_step` in `src/task_manager/storage/schema.sql` with `CREATE TABLE IF NOT EXISTS` only, as in `specs/031-workflow-checkpoints/data-model.md`. `UNIQUE (task_id, name)`. A step state is `Pending`, `Completed`, `Failed`, or `Waiting`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: A checkpoint and its step states can be stored and read.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T002 Read and insert checkpoints in `src/task_manager/storage/workflow_store.py`. A second insert for the same task and name does not add a row.

**Checkpoint**: A snapshot can be stored beside the workflow.

---

## Phase 3: User Story 1 - A named checkpoint stores the workflow (Priority: P1) 🎯 MVP

**Goal**: The engineer names a checkpoint and the original step states stay stored.

**Independent Test**: Take `before the read`, advance a step, and take the same name. The snapshot still shows the earlier states.

### Tests for User Story 1

- [X] T003 [P] [US1] Add the snapshot checks in `tests/unit/test_workflow_checkpoints.py`. Confirm they fail before the behavior exists.

### Implementation for User Story 1

- [X] T004 [US1] Add `take_checkpoint` in `src/task_manager/domain/workflow.py`. Use the sentences in `specs/031-workflow-checkpoints/contracts/commands.md`. Report `checkpoints` from the task detail.

**Checkpoint**: A rolled-back checkpoint leaves nothing stored.

---

## Phase 4: User Story 2 - Restore returns a failed step to the snapshot (Priority: P2)

**Goal**: Restore puts a failed step with no stored effect back to Pending.

**Independent Test**: Fail a second read after a checkpoint. Restore leaves the first read completed and the second step Pending.

### Tests for User Story 2

- [X] T005 [P] [US2] Extend `tests/unit/test_workflow_checkpoints.py` for restore, a stored effect, and a changed workflow.

### Implementation for User Story 2

- [X] T006 [US2] Add `restore_checkpoint` in `src/task_manager/domain/workflow.py`. Leave a completed step and a stored effect in place.

**Checkpoint**: Restore does not read the file again.

---

## Phase 5: User Story 3 - The task shows its checkpoints (Priority: P3)

**Goal**: The page shows the snapshot and can restore it.

**Independent Test**: The page says `No checkpoints yet.`, then shows the checkpoint after it is taken.

### Tests for User Story 3

- [X] T007 [P] [US3] Add `tests/contract/test_workflow_checkpoints_api.py` for the page, `POST /api/tasks/{id}/workflow/checkpoints`, and restore.

### Implementation for User Story 3

- [X] T008 [US3] Show checkpoints in `src/task_manager/web/templates/detail.html` and accept the commands in `src/task_manager/web/api.py`, `src/task_manager/web/pages.py`, and `src/task_manager/workspace.py`.

**Checkpoint**: The page and the command agree on the snapshot.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T009 Run the checks in `specs/031-workflow-checkpoints/quickstart.md` and confirm the existing suite stays green.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on T001. Blocks the stories.
- **User Story 1 (Phase 3)**: Depends on Phase 2.
- **User Story 2 (Phase 4)**: Depends on User Story 1, because restore uses a stored checkpoint.
- **User Story 3 (Phase 5)**: Depends on User Story 2, because the page can restore a checkpoint.
- **Polish (Phase 6)**: Depends on the stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Independently testable by taking a named checkpoint.
- **User Story 2 (P2)**: Independently testable once a snapshot exists.
- **User Story 3 (P3)**: Independently testable once restore is reported on the task.

### Parallel Opportunities

- T005 and T007 touch different test files and can be written together.

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete User Story 1.
3. Stop and validate the immutable snapshot.

### Incremental Delivery

1. Store a named snapshot.
2. Restore a failed step that has no stored effect.
3. Show the checkpoint on the task.

## Notes

- Do not make a completed step run again.
- Do not delete a stored file read.
- Commit only when the engineer asks.
