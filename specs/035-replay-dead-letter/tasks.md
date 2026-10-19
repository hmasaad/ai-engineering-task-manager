---
description: "Task list for Replay a Dead Letter"
---

# Tasks: Replay a Dead Letter

**Input**: Design documents from `/specs/035-replay-dead-letter/`

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

**Purpose**: The replay table. No existing table is altered.

- [X] T001 Add `workflow_dead_letter_replay` in `src/task_manager/storage/schema.sql` with `CREATE TABLE IF NOT EXISTS` only, as in `specs/035-replay-dead-letter/data-model.md`. `UNIQUE (task_id, name)`. `outbox_id` is unique. `name` is trimmed and not empty.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: One replay can be stored and read for a dead letter.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T002 Read and insert replays in `src/task_manager/storage/workflow_store.py`. A second insert for the same task and name does not add a row. A second insert for the same message does not add a row. `oldest_pending_outbox` skips a dead letter that has no replay and includes one that has a replay.

**Checkpoint**: A replay can be stored beside its dead letter.

---

## Phase 3: User Story 1 - Return the oldest dead letter to delivery (Priority: P1) 🎯 MVP

**Goal**: One named replay returns the oldest dead letter and a later delivery can accept it.

**Independent Test**: Replay "once". The message is Pending, the dead letter remains, and a delivery marks it Delivered.

### Tests for User Story 1

- [X] T003 [P] [US1] Add the replay and delivery checks in `tests/unit/test_replay_dead_letter.py`. Confirm they fail before the behavior exists.

### Implementation for User Story 1

- [X] T004 [US1] Return the oldest unreplayed dead letter in `src/task_manager/domain/workflow.py`. Pass the command through `src/task_manager/workspace.py`. A replayed message is shown as Pending. Delivery accepts it even when an earlier next time has not arrived. Do not change the attempt count.

**Checkpoint**: A delivery after the replay marks the message Delivered.

---

## Phase 4: User Story 2 - A replay that does not finish leaves the message Dead (Priority: P2)

**Goal**: A refusal or a rolled-back replay leaves the message Dead.

**Independent Test**: Roll back "once". The message stays Dead and delivery skips it.

### Tests for User Story 2

- [X] T005 [P] [US2] Extend `tests/unit/test_replay_dead_letter.py` for a blank name, no dead letter, a rolled-back replay, another task, and a task that is not In Progress.

### Implementation for User Story 2

- [X] T006 [US2] Store the replay only after the name is accepted in `src/task_manager/domain/workflow.py`. Use the sentences in `specs/035-replay-dead-letter/contracts/commands.md`. A Refusal leaves no row.

**Checkpoint**: A rolled-back replay leaves delivery unable to accept the message.

---

## Phase 5: User Story 3 - The task shows the replay (Priority: P3)

**Goal**: The page shows the replay and Replay dead letter.

**Independent Test**: The page offers Replay dead letter, and after "once" the message is Pending.

### Tests for User Story 3

- [X] T007 [P] [US3] Add `tests/contract/test_replay_dead_letter_api.py` for the page and `POST /api/tasks/{id}/workflow/dead-letters/replay`.

### Implementation for User Story 3

- [X] T008 [US3] Show Replayed dead letters in `src/task_manager/web/templates/detail.html`. Accept the command in `src/task_manager/web/api.py` and `src/task_manager/web/pages.py`. Include `dead_letter_replays` from `src/task_manager/domain/workflow.py`.

**Checkpoint**: The page and the command agree on the replay.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T009 Run the checks in `specs/035-replay-dead-letter/quickstart.md` and confirm the existing suite stays green.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on T001. Blocks the stories.
- **User Story 1 (Phase 3)**: Depends on Phase 2.
- **User Story 2 (Phase 4)**: Depends on User Story 1, because a rollback needs a replay that can be stored.
- **User Story 3 (Phase 5)**: Depends on User Story 1, because the page shows a stored replay.
- **Polish (Phase 6)**: Depends on the stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Independently testable by replaying one dead letter.
- **User Story 2 (P2)**: Independently testable once a replay can be stored.
- **User Story 3 (P3)**: Independently testable once the replay is on the task.

### Parallel Opportunities

- T005 and T007 touch different test files and can be written together.

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete User Story 1.
3. Stop and validate one replay and one delivery.

### Incremental Delivery

1. Return the oldest dead letter.
2. Leave a rolled-back replay Dead.
3. Show the replay on the task.

## Notes

- Do not delete the dead letter.
- Do not change the outbox state check.
- Do not reset the attempt count.
- Commit only when the engineer asks.
