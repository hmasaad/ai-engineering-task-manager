---
description: "Task list for Durable Workflow Orchestration"
---

# Tasks: Durable Workflow Orchestration

**Input**: Design documents from `/specs/020-durable-workflow/`

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

**Purpose**: The step table. `task` is not altered.

- [X] T001 Add `workflow_step` to `src/task_manager/storage/schema.sql` with `CREATE TABLE IF NOT EXISTS` only. Columns follow `specs/020-durable-workflow/data-model.md`. Add a unique index on `(task_id, position)`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: A task can be read with its workflow before the commands exist.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T002 Add `src/task_manager/storage/workflow_store.py` to insert one step, delete one step, list a task's steps by position, and update one step's state, detail, and change id. In `src/task_manager/storage/task_store.py`, add `workflow` to the task detail through `src/task_manager/domain/workflow.py`. An empty workflow has no steps, `stopped` null, `started` false, and `finished` false.

---

## Phase 3: User Story 1 - Store the steps before the run (Priority: P1)

**Goal**: An In Progress task stores ordered Pending steps and refuses a step that is not ready to store.

**Independent Test**: Add "Read the note" and "Create the folder". They stay in that order. A blank title stores nothing. A Pending step can be removed.

### Tests for User Story 1

- [X] T003 [P] [US1] Add failing tests in `tests/unit/test_workflow.py` and `tests/contract/test_workflow_api.py` for ordered steps, a blank title, an unknown action, a missing field, removal, a step that is not on the task, and a task that is not In Progress.

### Implementation for User Story 1

- [X] T004 [US1] Implement add and remove in `src/task_manager/domain/workflow.py`. Expose them from `src/task_manager/workspace.py`, `src/task_manager/web/api.py`, and `src/task_manager/web/pages.py`. Show the Workflow section in `src/task_manager/web/templates/detail.html` while every step is Pending.

**Checkpoint**: Steps can be stored and removed. Nothing is performed.

---

## Phase 4: User Story 2 - Advance one stored step and resume (Priority: P2)

**Goal**: One advance performs the first step that is not Completed. Reopening the workspace continues there. A Completed step is not performed again.

**Independent Test**: Advance a read, reopen the workspace file, and advance the following ordinary folder. The file is read once.

### Tests for User Story 2

- [X] T005 [US2] Extend `tests/unit/test_workflow.py` so one advance completes only the first step, reopening shows that state, the next advance performs the second step, and a finished workflow refuses with `There is no step to run.`

### Implementation for User Story 2

- [X] T006 [US2] Implement advance for a Pending read or ordinary folder in `src/task_manager/domain/workflow.py`. Add `POST /api/tasks/{task_id}/workflow/advance` and the Advance workflow button. Do not change the task status.

**Checkpoint**: A run resumes from the stored step.

---

## Phase 5: User Story 3 - Stop and name the step (Priority: P3)

**Goal**: A refused action and a consequential folder stop the run and name the step. Approval does not advance the workflow.

**Independent Test**: A missing file fails "Read the note" and leaves the next step Pending. A consequential folder waits, and the advance after approval completes that step only.

### Tests for User Story 3

- [X] T007 [US3] Extend `tests/unit/test_workflow.py` and `tests/contract/test_workflow_api.py` for the missing-file sentence, a retry that does not run the next step, a waiting folder that does not record a second change, and the advance after approval.

### Implementation for User Story 3

- [X] T008 [US3] Store Failed and Waiting in `src/task_manager/domain/workflow.py`. Settle a Waiting step from its `change_id`. Show `workflow.stopped` in `src/task_manager/web/templates/detail.html`.

**Checkpoint**: All three stories work. Task status commands stay unchanged.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T009 Run the full pytest suite.
- [X] T010 Check the Workflow section in the browser: add a consequential folder and a later read, advance until it waits, approve, advance once, and confirm the later step is still Pending.

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

- **User Story 1 (P1)**: First, because advance reads its stored steps
- **User Story 2 (P2)**: After User Story 1
- **User Story 3 (P3)**: After User Story 2, because waiting and failure use the same advance

### Parallel Opportunities

- T003 can be written against the contract before T004
- T005 and T007 extend the same test file, so they stay sequential

---

## Parallel Example: User Story 1

```bash
Task: "Unit tests in tests/unit/test_workflow.py"
Task: "Contract tests in tests/contract/test_workflow_api.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2
2. Complete User Story 1
3. Stop and validate a stored step and a refused blank title

### Incremental Delivery

1. User Story 1 stores the steps
2. User Story 2 advances one step and resumes
3. User Story 3 stops on a failure or an approval and names the step

---

## Notes

- [P] tasks = different files, no dependencies
- Do not change the task status from a workflow command
- Do not treat approval as an advance
- Do not wrap `GET /api/tasks` in a new object
- A failed or waiting advance returns the task detail so the step row is kept
