---
description: "Task list for Idempotency and Exactly-Once Effects"
---

# Tasks: Idempotency and Exactly-Once Effects

**Input**: Design documents from `/specs/022-exactly-once-effects/`

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

**Purpose**: The advance-name table. `task` and `workflow_step` gain no column.

- [X] T001 Add `workflow_advance` in `src/task_manager/storage/schema.sql` with `CREATE TABLE IF NOT EXISTS` only, primary key `(task_id, name)`, `name` trimmed and not empty, and `step_id` referencing `workflow_step(id)`, as in `specs/022-exactly-once-effects/data-model.md`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The workspace can store and read one advance name before either story changes an advance.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T002 Add insert and lookup of one `(task_id, name, step_id)` row in `src/task_manager/storage/workflow_store.py`. A duplicate primary key is reported to the caller. A blank name is not inserted.

**Checkpoint**: The name can be stored. No advance behavior changes yet.

---

## Phase 3: User Story 1 - One effect for one step (Priority: P1) 🎯 MVP

**Goal**: A step with a stored file read or folder change is not performed again.

**Independent Test**: Finish a running read whose file read is already stored. The step is Completed and the file is read once. Advance again after a declined folder. One change remains, the stop sentence stays `Stopped at Create the folder: Not this folder`, and the next step stays Pending.

### Tests for User Story 1

- [X] T003 [P] [US1] Write the stored-read and declined-folder checks in `tests/unit/test_exactly_once.py`. Confirm they fail before the behavior exists.

### Implementation for User Story 1

- [X] T004 [US1] In `src/task_manager/domain/workflow.py`, settle a running step from the attempt baseline before performing the action. A Failed step whose `change_id` is set stays Failed, records no second change, and adds no replay entry.

**Checkpoint**: One effect per step. Unnamed advances of a failure with no effect still retry.

---

## Phase 4: User Story 2 - The same advance name performs one step (Priority: P2)

**Goal**: The first accepted use of a name performs one step. The same name does not perform another.

**Independent Test**: Advance with "once" through a read. The folder step stays Pending. "once" again adds no replay entry. A different name creates the folder. A blank second advance can perform the next step. The same name on another task still runs.

### Tests for User Story 2

- [X] T005 [P] [US2] Extend `tests/unit/test_exactly_once.py` for a repeated name, a blank name, another task, and a name that is not saved when the task is not In Progress.
- [X] T006 [P] [US2] Add `tests/contract/test_exactly_once_api.py` for `POST /api/tasks/{id}/workflow/advance` with `name`, a missing body, and `GET /api/tasks` remaining a list.

### Implementation for User Story 2

- [X] T007 [US2] Pass an optional name through `src/task_manager/workspace.py` and `src/task_manager/web/api.py`. In `src/task_manager/domain/workflow.py`, save the trimmed name when the advance is accepted, and on a repeat settle only that step or return the task without a new effect. A blank name is not saved. A refusal that stores nothing does not save the name.

**Checkpoint**: The same name performs one step. A blank name keeps the current advance rules.

---

## Phase 5: User Story 3 - The page supplies the advance name (Priority: P3)

**Goal**: The task page shows Advance name and supplies a new name each time the task is shown.

**Independent Test**: The advance form contains a filled-in name. Submitting a name that already advanced leaves the next step pending.

### Tests for User Story 3

- [X] T008 [P] [US3] In `tests/contract/test_exactly_once_api.py`, assert the task page shows `Advance name` and that posting a used name leaves the next step pending.

### Implementation for User Story 3

- [X] T009 [US3] Fill `name` on the advance form in `src/task_manager/web/pages.py` and `src/task_manager/web/templates/detail.html`. Label `Advance name`, id `advance-name`. Supply a new non-empty value each time the task is shown.

**Checkpoint**: The page name and the command name follow the same rule.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T010 Run the checks in `specs/022-exactly-once-effects/quickstart.md` and confirm the existing suite stays green.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on T001. Blocks the stories.
- **User Story 1 (Phase 3)**: Depends on Phase 2.
- **User Story 2 (Phase 4)**: Depends on Phase 2 and uses the effect rule from User Story 1.
- **User Story 3 (Phase 5)**: Depends on User Story 2, because the page posts the name that story understands.
- **Polish (Phase 6)**: Depends on the stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Independently testable with an unnamed advance.
- **User Story 2 (P2)**: Independently testable through the advance name. A repeat must also avoid a second effect.
- **User Story 3 (P3)**: Depends on the name the command accepts.

### Parallel Opportunities

- T005 and T006 touch different test files and can be written together.
- T003 is the only User Story 1 test file.

### Parallel Example: User Story 2

```bash
# Tests in different files:
tests/unit/test_exactly_once.py
tests/contract/test_exactly_once_api.py
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete User Story 1.
3. Stop and validate one effect per step.

### Incremental Delivery

1. Setup and the name store.
2. User Story 1: a stored effect is not repeated.
3. User Story 2: the same name performs one step.
4. User Story 3: the page supplies the name.

## Notes

- Unnamed advances stay compatible with specifications 001 through 021.
- Do not add a column to `workflow_step`.
- Commit only when the engineer asks.
