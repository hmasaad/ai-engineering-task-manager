---
description: "Task list for Work Stealing, Backpressure, and Load Balancing"
---

# Tasks: Work Stealing, Backpressure, and Load Balancing

**Input**: Design documents from `/specs/037-balance-workers/`

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

**Purpose**: The worker, job, and steal tables. No existing table is altered.

- [X] T001 Add `work_worker`, `work_job`, and `work_steal` in `src/task_manager/storage/schema.sql` with `CREATE TABLE IF NOT EXISTS` only, as in `specs/037-balance-workers/data-model.md`. `UNIQUE (task_id, name)` on each. `name` is trimmed and not empty. `work_job.worker_id` is required.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Workers, jobs, and steals can be stored and read for a task.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T002 Read and insert workers, jobs, and steals in `src/task_manager/storage/worker_store.py`. A second insert for the same task and name does not add a row. Moving a job changes `worker_id`. Return workers oldest first with their jobs oldest first, and steals oldest first.

**Checkpoint**: A worker can be stored beside the jobs it holds.

---

## Phase 3: User Story 1 - Place a job on the least busy worker (Priority: P1) 🎯 MVP

**Goal**: One named job goes to the worker with the fewest pending jobs. The worker named first wins a tie.

**Independent Test**: Place "one", "two", and "three" on ada and grace. Ada holds "one" and "three". Grace holds "two".

### Tests for User Story 1

- [X] T003 [P] [US1] Add the balance checks in `tests/unit/test_balance_workers.py`. Confirm they fail before the behavior exists.

### Implementation for User Story 1

- [X] T004 [US1] Name a worker and place a job in `src/task_manager/domain/workers.py`. Pass the commands through `src/task_manager/workspace.py`. Include `work` on the task detail from `src/task_manager/storage/task_store.py`. Equal counts choose the earliest worker. The same name does not add a second row.

**Checkpoint**: A third job lands on the worker named first.

---

## Phase 4: User Story 2 - A full queue refuses more work (Priority: P2)

**Goal**: The fourth job on a worker who already holds three is refused, and a rolled-back placement leaves no job.

**Independent Test**: Place three jobs on one worker. The fourth is refused with `Every worker is full.`

### Tests for User Story 2

- [X] T005 [P] [US2] Extend `tests/unit/test_balance_workers.py` for a full queue, two full workers, a blank name, no worker, a rolled-back placement, another task, and a task that is not In Progress.

### Implementation for User Story 2

- [X] T006 [US2] Refuse a placement when the least-loaded worker holds three jobs in `src/task_manager/domain/workers.py`. Use the sentences in `specs/037-balance-workers/contracts/commands.md`. A Refusal leaves no row.

**Checkpoint**: A full queue leaves the three jobs in place.

---

## Phase 5: User Story 3 - An idle worker takes the oldest job (Priority: P3)

**Goal**: A named idle worker takes the oldest job from the busiest other worker, and the page shows the queues.

**Independent Test**: Lin steals "take" and holds ada's oldest job. The page shows that steal.

### Tests for User Story 3

- [X] T007 [P] [US3] Extend `tests/unit/test_balance_workers.py` for a steal, a tie, a repeated steal, a worker who is not idle, a rolled-back steal, and a task that is not In Progress. Add `tests/contract/test_balance_workers_api.py` for the page and the three commands.

### Implementation for User Story 3

- [X] T008 [US3] Steal one job in `src/task_manager/domain/workers.py`. Show Workers in `src/task_manager/web/templates/detail.html`. Accept the commands in `src/task_manager/web/api.py` and `src/task_manager/web/pages.py`.

**Checkpoint**: The page and the command agree on the steal.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T009 Run the checks in `specs/037-balance-workers/quickstart.md` and confirm the existing suite stays green.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on T001. Blocks the stories.
- **User Story 1 (Phase 3)**: Depends on Phase 2.
- **User Story 2 (Phase 4)**: Depends on User Story 1, because a full queue needs a placement.
- **User Story 3 (Phase 5)**: Depends on User Story 1, because a steal needs a job to move.
- **Polish (Phase 6)**: Depends on the stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Independently testable by placing three jobs.
- **User Story 2 (P2)**: Independently testable once a job can be stored.
- **User Story 3 (P3)**: Independently testable once a job can be stored.

### Parallel Opportunities

- T003 can be written while T002 is reviewed, and it fails until T004.
- T005 and T007 touch the same test file, so they stay sequential.

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete User Story 1 and confirm ada holds "one" and "three".
3. Add the bound, then the steal and the page.

### Incremental Delivery

1. Setup and store methods.
2. User Story 1: load balancing.
3. User Story 2: backpressure.
4. User Story 3: work stealing and the page.
5. The full pytest suite.
