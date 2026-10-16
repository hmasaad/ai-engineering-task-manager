---
description: "Task list for Dead Letter Queues and Poison Messages"
---

# Tasks: Dead Letter Queues and Poison Messages

**Input**: Design documents from `/specs/029-dead-letter-queue/`

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

**Purpose**: The poison and dead-letter tables. No existing table is altered.

- [X] T001 Add `workflow_poison` and `workflow_dead_letter` in `src/task_manager/storage/schema.sql` with `CREATE TABLE IF NOT EXISTS` only, as in `specs/029-dead-letter-queue/data-model.md`. `workflow_poison` uses `PRIMARY KEY (task_id, name)`. `workflow_dead_letter.outbox_id` is unique. `reason` is trimmed and not empty on both tables.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: A rejection and a dead letter can be stored and read for one outbox message.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T002 Read and insert poison rejections and dead letters in `src/task_manager/storage/workflow_store.py`. A second insert for the same task and name does not add a row. `oldest_pending_outbox` skips a message that already has a dead letter.

**Checkpoint**: A rejection can be stored beside its outbox message.

---

## Phase 3: User Story 1 - The third rejection dead-letters the oldest message (Priority: P1) 🎯 MVP

**Goal**: The third rejection sets the oldest Pending message aside, and the next message can be delivered.

**Independent Test**: Reject two completed reads until the older one is a dead letter. Deliver the newer one.

### Tests for User Story 1

- [X] T003 [P] [US1] Add the third-rejection checks in `tests/unit/test_dead_letter.py`. Confirm they fail before the behavior exists.

### Implementation for User Story 1

- [X] T004 [US1] Add `reject` in `src/task_manager/domain/workflow.py`. The third rejection of one message stores one dead letter with that reason. Report `poison` and `dead_letters` from the task detail, and show that outbox message as Dead.

**Checkpoint**: One or two rejections still leave the message deliverable.

---

## Phase 4: User Story 2 - A rejection is counted once (Priority: P2)

**Goal**: A repeated name, a blank field, and a rolled-back rejection do not change the poison count.

**Independent Test**: Reject `once` twice. The message has one rejection. A rolled-back third rejection leaves no dead letter.

### Tests for User Story 2

- [X] T005 [P] [US2] Extend `tests/unit/test_dead_letter.py` for a repeated name, the refusal sentences in `specs/029-dead-letter-queue/contracts/commands.md`, another task, and a rolled-back rejection.

### Implementation for User Story 2

- [X] T006 [US2] Refuse a blank name with `Name this rejection.`, a blank reason with `Name why this message is poison.`, and an empty queue with `There is no outbox message to reject.` The same name returns the task detail without another row.

**Checkpoint**: A repeated name does not dead-letter the message.

---

## Phase 5: User Story 3 - The task shows poison messages and dead letters (Priority: P3)

**Goal**: The page shows rejections, dead letters, and Reject message.

**Independent Test**: The page offers Reject message, then shows the dead letter after three rejections.

### Tests for User Story 3

- [X] T007 [P] [US3] Add `tests/contract/test_dead_letter_api.py` for the page and `POST /api/tasks/{id}/workflow/outbox/reject`.

### Implementation for User Story 3

- [X] T008 [US3] Show poison rejections and dead letters in `src/task_manager/web/templates/detail.html` and accept the command in `src/task_manager/web/api.py`, `src/task_manager/web/pages.py`, and `src/task_manager/workspace.py`.

**Checkpoint**: The page and the command agree on the dead letter.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T009 Run the checks in `specs/029-dead-letter-queue/quickstart.md` and confirm the existing suite stays green.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on T001. Blocks the stories.
- **User Story 1 (Phase 3)**: Depends on Phase 2.
- **User Story 2 (Phase 4)**: Depends on User Story 1, because the repeated name uses the same rejection.
- **User Story 3 (Phase 5)**: Depends on User Story 2, because the page can show a dead letter.
- **Polish (Phase 6)**: Depends on the stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Independently testable by dead-lettering the oldest message.
- **User Story 2 (P2)**: Independently testable once a rejection can be recorded.
- **User Story 3 (P3)**: Independently testable once the dead letter is reported.

### Parallel Opportunities

- T005 and T007 touch different test files and can be written together.

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete User Story 1.
3. Stop and validate the third rejection.

### Incremental Delivery

1. Dead-letter the oldest message on the third rejection.
2. Count each rejection name once.
3. Show the dead letter on the task.

## Notes

- Do not delete the outbox message.
- Do not change the stored outbox state check.
- Commit only when the engineer asks.
