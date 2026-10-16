---
description: "Task list for Transactional Outbox and Inbox"
---

# Tasks: Transactional Outbox and Inbox

**Input**: Design documents from `/specs/027-transactional-outbox/`

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

**Purpose**: The outbox and inbox tables. No existing table is altered.

- [X] T001 Add `workflow_outbox` and `workflow_inbox` in `src/task_manager/storage/schema.sql` with `CREATE TABLE IF NOT EXISTS` only, as in `specs/027-transactional-outbox/data-model.md`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The workflow can store and read one message per step.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T002 Read and insert outbox and inbox rows in `src/task_manager/storage/workflow_store.py`. A second insert for the same step or the same delivery name does not add a row.

**Checkpoint**: A message can be stored and read with its step.

---

## Phase 3: User Story 1 - A completed step stores one outbox message (Priority: P1) 🎯 MVP

**Goal**: Completion stores one Pending message, and a rolled-back completion stores none.

**Independent Test**: Complete one read and see one Pending message for that file. Fail a missing file and see no message.

### Tests for User Story 1

- [X] T003 [P] [US1] Add the completion and rollback checks in `tests/unit/test_transactional_outbox.py`. Confirm they fail before the behavior exists.

### Implementation for User Story 1

- [X] T004 [US1] Store the message from `src/task_manager/domain/workflow.py` in the same completion as the step. Report `outbox` from the task detail.

**Checkpoint**: A refused completion leaves no message.

---

## Phase 4: User Story 2 - A named delivery is accepted once (Priority: P2)

**Goal**: A delivery name delivers the oldest Pending message once.

**Independent Test**: Two completed reads. `once` delivers the first. `once` again leaves the second Pending. `next` delivers the second.

### Tests for User Story 2

- [X] T005 [P] [US2] Extend `tests/unit/test_transactional_outbox.py` for a repeated name, a blank name, an empty outbox, and the same name on another task.

### Implementation for User Story 2

- [X] T006 [US2] Add `deliver` in `src/task_manager/domain/workflow.py` and `deliver_outbox` in `src/task_manager/workspace.py` using the sentences in `specs/027-transactional-outbox/contracts/commands.md`.

**Checkpoint**: A repeated name does not deliver a second message.

---

## Phase 5: User Story 3 - The task shows the outbox and the inbox (Priority: P3)

**Goal**: The page shows the messages and accepts one delivery name.

**Independent Test**: The page shows a Pending message, Deliver outbox, and the inbox name `once` after delivery.

### Tests for User Story 3

- [X] T007 [P] [US3] Add `tests/contract/test_transactional_outbox_api.py` for the page and `POST /api/tasks/{id}/workflow/outbox`.

### Implementation for User Story 3

- [X] T008 [US3] Show the outbox and inbox in `src/task_manager/web/templates/detail.html` and accept the command in `src/task_manager/web/api.py` and `src/task_manager/web/pages.py`.

**Checkpoint**: The page and the command agree on which message is Delivered.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T009 Run the checks in `specs/027-transactional-outbox/quickstart.md` and confirm the existing suite stays green.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on T001. Blocks the stories.
- **User Story 1 (Phase 3)**: Depends on Phase 2.
- **User Story 2 (Phase 4)**: Depends on User Story 1, because delivery needs a Pending message.
- **User Story 3 (Phase 5)**: Depends on User Story 2, because the page posts the delivery name.
- **Polish (Phase 6)**: Depends on the stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Independently testable by completing a step.
- **User Story 2 (P2)**: Independently testable once a message is Pending.
- **User Story 3 (P3)**: Independently testable once a name can be delivered.

### Parallel Opportunities

- T005 and T007 touch different test files and can be written together.

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete User Story 1.
3. Stop and validate one message per completed step.

### Incremental Delivery

1. Store the message with the completion.
2. Accept each delivery name once.
3. Show both lists on the task.

## Notes

- A rolled-back completion must not leave a message.
- Do not perform the step during delivery.
- Commit only when the engineer asks.
