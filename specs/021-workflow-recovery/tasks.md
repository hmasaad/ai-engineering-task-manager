---
description: "Task list for Workflow Recovery and Replay"
---

# Tasks: Workflow Recovery and Replay

**Input**: Design documents from `/specs/021-workflow-recovery/`

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

**Purpose**: The replay tables. `task` gains no column.

- [X] T001 In `src/task_manager/storage/schema.sql`, allow `Running` on a new `workflow_step` table. Add `workflow_attempt` and `workflow_event` with `CREATE TABLE IF NOT EXISTS` only, as in `specs/021-workflow-recovery/data-model.md`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: A task can be read with its replay before recovery exists.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T002 Extend `src/task_manager/storage/workflow_store.py` to insert and delete an attempt, insert an event, and list events by id with the step title. Add `replay` and `interrupted` to the workflow payload in `src/task_manager/domain/workflow.py`.

---

## Phase 3: User Story 1 - Read the replay (Priority: P1)

**Goal**: An advance stores a running entry and a result entry. Reading them performs nothing.

**Independent Test**: Advance a read of a file that exists. The replay has running, then completed. Reopening the workspace shows the same list and the same one file read.

### Tests for User Story 1

- [X] T003 [P] [US1] Add failing tests in `tests/unit/test_workflow_recovery.py` and `tests/contract/test_workflow_recovery_api.py` for an empty replay, a running-then-completed replay, and the same replay after the workspace is opened again.

### Implementation for User Story 1

- [X] T004 [US1] Split advance in `src/task_manager/domain/workflow.py` so the running entry commits before the result. Expose `GET /api/tasks/{task_id}/workflow-replay` from `src/task_manager/web/api.py` and `src/task_manager/workspace.py`. Show `Replay` in `src/task_manager/web/templates/detail.html`.

**Checkpoint**: The replay can be read and does not perform a step.

---

## Phase 4: User Story 2 - Recover an interrupted step (Priority: P2)

**Goal**: A running step with no effect is recovered as failed, and advance will not perform it.

**Independent Test**: Leave a read running. Advance is refused. Recover reports `Stopped at Read the note: the step was interrupted.` and leaves the next step pending.

### Tests for User Story 2

- [X] T005 [US2] Extend the recovery tests for a running step, `Recover the interrupted step first.`, `There is no step to recover.`, and a retry that performs only that step.

### Implementation for User Story 2

- [X] T006 [US2] Implement recover in `src/task_manager/domain/workflow.py`. Add `POST /api/tasks/{task_id}/workflow/recover`, the page route in `src/task_manager/web/pages.py`, and the Recover workflow button. Hide Advance workflow while a step is running.

**Checkpoint**: An interrupted step can be recovered without performing the next step.

---

## Phase 5: User Story 3 - Recover from a stored effect (Priority: P3)

**Goal**: A stored file read or folder change settles the running step without a second effect.

**Independent Test**: Store the file read while the step is running. Recover marks it completed and leaves one file read.

### Tests for User Story 3

- [X] T007 [US3] Extend the recovery tests for a stored file read and a stored consequential folder. The file is not read again, and the folder change is not recorded again.

### Implementation for User Story 3

- [X] T008 [US3] In `src/task_manager/domain/workflow.py`, settle a running step from the attempt baseline. Do not call the read or folder command when the effect is already stored.

**Checkpoint**: All three stories work. Task status commands stay unchanged.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T009 Run the full pytest suite.
- [X] T010 Check the task page: the replay lists a completed read, an interrupted step shows Recover workflow, and recover leaves the next step pending.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup
- **User Story 1 (Phase 3)**: Depends on Foundational
- **User Story 2 (Phase 4)**: Depends on User Story 1
- **User Story 3 (Phase 5)**: Depends on User Story 2
- **Polish (Phase 6)**: Depends on all stories

### User Story Dependencies

- **User Story 1 (P1)**: First, because recovery appends to the replay
- **User Story 2 (P2)**: After the running entry can be stored
- **User Story 3 (P3)**: After recover exists for a step with no effect

### Parallel Opportunities

- T003 can be written against the contract before T004
- T005 and T007 extend the same test file, so they stay sequential

---

## Parallel Example: User Story 1

```bash
Task: "Unit tests in tests/unit/test_workflow_recovery.py"
Task: "Contract tests in tests/contract/test_workflow_recovery_api.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2
2. Complete User Story 1
3. Stop and validate a replay that does not perform a step

### Incremental Delivery

1. User Story 1 stores and reads the replay
2. User Story 2 recovers an interrupted step
3. User Story 3 recovers from a stored effect

---

## Notes

- [P] tasks = different files, no dependencies
- Do not change the task status from replay or recover
- Do not approve a change from recover
- Do not wrap `GET /api/tasks` in a new object
- The running entry commits before the result
