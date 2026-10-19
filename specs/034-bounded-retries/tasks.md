---
description: "Task list for Bounded Delivery Retries"
---

# Tasks: Bounded Delivery Retries

**Input**: Design documents from `/specs/034-bounded-retries/`

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

**Purpose**: The attempt table. No existing table is altered.

- [X] T001 Add `workflow_delivery_retry` in `src/task_manager/storage/schema.sql` with `CREATE TABLE IF NOT EXISTS` only, as in `specs/034-bounded-retries/data-model.md`. `UNIQUE (task_id, name)`. `name` and `next_eligible_at` are trimmed and not empty.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: One attempt can be stored and counted for a message.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T002 Read, insert, and count attempts in `src/task_manager/storage/workflow_store.py`. A second insert for the same task and name does not add a row. The count for one message stops being read as more than the rows that exist.

**Checkpoint**: An attempt can be stored beside its message.

---

## Phase 3: User Story 1 - An unsuccessful delivery waits one minute (Priority: P1) 🎯 MVP

**Goal**: One named unsuccessful delivery waits one minute. An early delivery does not count.

**Independent Test**: Record "once". Deliver before the next time. The message stays Pending and the count stays 1.

### Tests for User Story 1

- [X] T003 [P] [US1] Add the wait and the due delivery checks in `tests/unit/test_bounded_retries.py`. Confirm they fail before the behavior exists.

### Implementation for User Story 1

- [X] T004 [US1] Record one attempt and refuse an early delivery in `src/task_manager/domain/workflow.py`. Pass the command through `src/task_manager/workspace.py`. The next time is one minute later. The bound is not reached yet.

**Checkpoint**: A delivery before the next time leaves the count unchanged.

---

## Phase 4: User Story 2 - The third attempt writes the dead letter (Priority: P2)

**Goal**: The third attempt writes the existing dead letter. A rolled-back third attempt does not.

**Independent Test**: Three attempts show Dead and a count of 3. A rolled-back third attempt leaves a count of 2 and no dead letter.

### Tests for User Story 2

- [X] T005 [P] [US2] Extend `tests/unit/test_bounded_retries.py` for the third attempt, a rolled-back third attempt, another task, and a repeated delivery name.

### Implementation for User Story 2

- [X] T006 [US2] Write the existing dead letter in the same result as the third attempt in `src/task_manager/domain/workflow.py`. Use the reason `The delivery was attempted too many times.` Do not change `workflow_outbox.state`.

**Checkpoint**: A rolled-back third attempt leaves no dead letter.

---

## Phase 5: User Story 3 - The task shows the attempts (Priority: P3)

**Goal**: The page shows the count, the next time, and Delivery did not succeed.

**Independent Test**: The page shows attempt count 1, and an early attempt from the page does not increase it.

### Tests for User Story 3

- [X] T007 [P] [US3] Add `tests/contract/test_bounded_retries_api.py` for the page, `POST /api/tasks/{id}/workflow/outbox/retry`, and an early `POST /api/tasks/{id}/workflow/outbox`.

### Implementation for User Story 3

- [X] T008 [US3] Show Delivery attempts in `src/task_manager/web/templates/detail.html`. Accept the command in `src/task_manager/web/api.py` and `src/task_manager/web/pages.py`. Include `retries` from `src/task_manager/domain/workflow.py`.

**Checkpoint**: The page and the command agree on the attempt count.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T009 Run the checks in `specs/034-bounded-retries/quickstart.md` and confirm the existing suite stays green.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on T001. Blocks the stories.
- **User Story 1 (Phase 3)**: Depends on Phase 2.
- **User Story 2 (Phase 4)**: Depends on User Story 1, because the third attempt needs the first two.
- **User Story 3 (Phase 5)**: Depends on User Story 1, because the page shows a stored attempt.
- **Polish (Phase 6)**: Depends on the stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Independently testable by recording one attempt.
- **User Story 2 (P2)**: Independently testable once an attempt can be stored.
- **User Story 3 (P3)**: Independently testable once the count is on the task.

### Parallel Opportunities

- T005 and T007 touch different test files and can be written together.

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete User Story 1.
3. Stop and validate one attempt and one early refusal.

### Incremental Delivery

1. Record the attempt and the next time.
2. Write the dead letter on the third attempt.
3. Show the attempt on the task.

## Notes

- Do not change the outbox state check.
- Do not replay a dead letter.
- Commit only when the engineer asks.
