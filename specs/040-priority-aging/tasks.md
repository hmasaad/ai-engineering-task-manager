---
description: "Task list for Priority Scheduling, Aging, and Starvation Prevention"
---

# Tasks: Priority Scheduling, Aging, and Starvation Prevention

**Input**: Design documents from `/specs/040-priority-aging/`

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

**Purpose**: The ranked-work and serve tables. No existing table is altered.

- [X] T001 Add `priority_work` and `priority_serve` in `src/task_manager/storage/schema.sql` with `CREATE TABLE IF NOT EXISTS` only, as in `specs/040-priority-aging/data-model.md`. `UNIQUE (task_id, name)` on each table. `priority_work.rank` is an integer in (1, 2, 3). `priority_work.age` is an integer greater than or equal to 0.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Ranked work and serves can be stored and read oldest first.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T002 Read and insert ranked work and serves in `src/task_manager/storage/priority_store.py`. A second insert for the same task and name does not add a row. Return waiting work and serves oldest first. Age other waiting rows by 1 when a serve is stored.

**Checkpoint**: Work can be stored without a serve.

---

## Phase 3: User Story 1 - Rank waiting work (Priority: P1) 🎯 MVP

**Goal**: A named piece of work starts at the given rank and age 0.

**Independent Test**: Rank " quiet " at 1 and "rush" at 3. Rank "quiet" at 3 again. Quiet stays at rank 1, age 0.

### Tests for User Story 1

- [X] T003 [P] [US1] Add the ranking checks in `tests/unit/test_priority_aging.py`. Confirm they fail before the behavior exists.

### Implementation for User Story 1

- [X] T004 [US1] Rank work in `src/task_manager/domain/priority.py`. Pass the command through `src/task_manager/workspace.py`. Include `priority` on the task detail from `src/task_manager/storage/task_store.py`. Rank is 1, 2, or 3. Age starts at 0.

**Checkpoint**: A second ranking of the same name changes no rank and no age.

---

## Phase 4: User Story 2 - Serve the highest score and age the rest (Priority: P2)

**Goal**: A named serve goes to the highest score. Every other waiting piece ages by 1.

**Independent Test**: Quiet at rank 1 and rush at rank 3. Serve "one" serves rush and leaves quiet at age 1.

### Tests for User Story 2

- [X] T005 [P] [US2] Extend `tests/unit/test_priority_aging.py` for a highest-score serve, a repeated serve, no waiting work, and a rolled-back serve.

### Implementation for User Story 2

- [X] T006 [US2] Serve one piece of work in `src/task_manager/domain/priority.py`. Use the sentences in `specs/040-priority-aging/contracts/commands.md`. The serve and the age of the other waiting work commit together. A Refusal leaves no row and changes no age.

**Checkpoint**: Equal scores choose the work stored first.

---

## Phase 5: User Story 3 - Keep low rank from waiting forever (Priority: P3)

**Goal**: Rank-1 work aged by 2 is served ahead of new rank-3 work. The page shows the schedule.

**Independent Test**: After quiet is at age 2, serving "three" serves quiet ahead of late at rank 3. The page shows `three served quiet`.

### Tests for User Story 3

- [X] T007 [P] [US3] Extend `tests/unit/test_priority_aging.py` for the starvation tie, a blank serve, and another task. Add `tests/contract/test_priority_aging_api.py` for the page and the two commands.

### Implementation for User Story 3

- [X] T008 [US3] Choose the earlier work when scores tie in `src/task_manager/domain/priority.py`. Show the priority schedule in `src/task_manager/web/templates/detail.html`. Accept the commands in `src/task_manager/web/api.py` and `src/task_manager/web/pages.py`.

**Checkpoint**: The page and the command agree on which work was served.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T009 Run the checks in `specs/040-priority-aging/quickstart.md` and confirm the existing suite stays green.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on T001. Blocks the stories.
- **User Story 1 (Phase 3)**: Depends on Phase 2.
- **User Story 2 (Phase 4)**: Depends on User Story 1, because a serve needs ranked work.
- **User Story 3 (Phase 5)**: Depends on User Story 2, because the page shows a serve.
- **Polish (Phase 6)**: Depends on the stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Independently testable by ranking two pieces of work.
- **User Story 2 (P2)**: Independently testable once work can be ranked.
- **User Story 3 (P3)**: Independently testable once a serve can age the rest.

### Parallel Opportunities

- T003 can be written while T002 is reviewed, and it fails until T004.
- T005 and T007 touch the same test file, so they stay sequential.

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete User Story 1 and confirm each piece of work starts at the given rank and age 0.
3. Add the highest-score serve, then the starvation tie and the page.

### Incremental Delivery

1. Setup and store methods.
2. User Story 1: rank work.
3. User Story 2: serve the highest score and age the rest.
4. User Story 3: serve aged low rank ahead of new high rank, and show the page.
5. The full pytest suite.
