---
description: "Task list for Autoscaling and Queue-Based Capacity Planning"
---

# Tasks: Autoscaling and Queue-Based Capacity Planning

**Input**: Design documents from `/specs/038-scale-capacity/`

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

**Purpose**: The queue, plan, scale, and release tables. No existing table is altered.

- [X] T001 Add `work_queue`, `work_plan`, `work_scale`, and `work_release` in `src/task_manager/storage/schema.sql` with `CREATE TABLE IF NOT EXISTS` only, as in `specs/038-scale-capacity/data-model.md`. `UNIQUE (task_id, name)` on the queue, the plan, and the scale. `work_release.worker_id` is unique.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Waiting work, plans, scales, and releases can be stored and read. Active workers exclude a release.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T002 Read and insert the queue, plans, scales, and releases in `src/task_manager/storage/worker_store.py`. A second insert for the same task and name does not add a row. Return waiting names, plans, and scales oldest first. An active worker has no release row.

**Checkpoint**: A queued name can be stored without a worker.

---

## Phase 3: User Story 1 - Read how many workers the queue needs (Priority: P1) 🎯 MVP

**Goal**: A named plan records waiting, held, active, and workers needed.

**Independent Test**: Queue four items and plan "now". The plan says 4 waiting, 0 held, 2 needed, and 0 active.

### Tests for User Story 1

- [X] T003 [P] [US1] Add the queue and plan checks in `tests/unit/test_scale_capacity.py`. Confirm they fail before the behavior exists.

### Implementation for User Story 1

- [X] T004 [US1] Queue work and record a plan in `src/task_manager/domain/workers.py`. Pass the commands through `src/task_manager/workspace.py`. Include `queue`, `plans`, `needed`, and `active` on `work`. One worker is needed for every three waiting or held items.

**Checkpoint**: A second plan name records its own reading.

---

## Phase 4: User Story 2 - Add a worker only when the queue is past capacity (Priority: P2)

**Goal**: A scale fills spare room before it adds one worker.

**Independent Test**: Ada takes "one" from the queue. After ada holds three, "grace" is added and holds the next waiting item.

### Tests for User Story 2

- [X] T005 [P] [US2] Extend `tests/unit/test_scale_capacity.py` for a fill, a scale-up, a repeated scale, a rolled-back scale, a taken worker name, and a task that is not In Progress.

### Implementation for User Story 2

- [X] T006 [US2] Assign or add one worker in `src/task_manager/domain/workers.py`. Use the sentences in `specs/038-scale-capacity/contracts/commands.md`. The assignment and the scale commit together. A Refusal leaves no row.

**Checkpoint**: A full worker gains one new worker for the oldest waiting item.

---

## Phase 5: User Story 3 - Release an idle worker the queue does not need (Priority: P3)

**Goal**: A scale releases the newest idle worker when fewer workers are needed, and the page shows the capacity.

**Independent Test**: Grace is released while ada stays. The page shows the plan and the release.

### Tests for User Story 3

- [X] T007 [P] [US3] Extend `tests/unit/test_scale_capacity.py` for a release, a worker who holds a job, a matched queue, a rolled-back release, and another task. Add `tests/contract/test_scale_capacity_api.py` for the page and the three commands.

### Implementation for User Story 3

- [X] T008 [US3] Release one idle worker in `src/task_manager/domain/workers.py`. Ignore released workers in placement and stealing. Show the capacity in `src/task_manager/web/templates/detail.html`. Accept the commands in `src/task_manager/web/api.py` and `src/task_manager/web/pages.py`.

**Checkpoint**: The page and the command agree on the release.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T009 Run the checks in `specs/038-scale-capacity/quickstart.md` and confirm the existing suite stays green.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on T001. Blocks the stories.
- **User Story 1 (Phase 3)**: Depends on Phase 2.
- **User Story 2 (Phase 4)**: Depends on User Story 1, because a scale assigns queued work.
- **User Story 3 (Phase 5)**: Depends on User Story 2, because the page shows a scale.
- **Polish (Phase 6)**: Depends on the stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Independently testable by planning four waiting items.
- **User Story 2 (P2)**: Independently testable once work can be queued.
- **User Story 3 (P3)**: Independently testable once a scale can be stored.

### Parallel Opportunities

- T003 can be written while T002 is reviewed, and it fails until T004.
- T005 and T007 touch the same test file, so they stay sequential.

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete User Story 1 and confirm the plan says 2 workers are needed.
3. Add the fill and the scale-up, then the release and the page.

### Incremental Delivery

1. Setup and store methods.
2. User Story 1: the capacity plan.
3. User Story 2: fill, then scale up.
4. User Story 3: release and the page.
5. The full pytest suite.
