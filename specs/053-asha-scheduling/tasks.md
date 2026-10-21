# Tasks: Asynchronous Hyperband, ASHA, and Distributed Agent Scheduling

**Input**: Design documents from `/specs/053-asha-scheduling/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/commands.md

**Tests**: Test-first. The checks in T002 and T003 MUST fail before T004 through T008 are implemented.

## Phase 1: Setup

- [X] T001 Confirm `specs/053-asha-scheduling/plan.md`, `research.md`, `data-model.md`, `contracts/commands.md`, and `quickstart.md` exist.

## Phase 2: Foundational

- [X] T002 Write failing unit checks in `tests/unit/test_asha_scheduling.py` for four trials, two runners, a rung score, early promotion, the least-loaded runner, a winner, and a rolled-back rung score (FR-001, FR-002, FR-003).
- [X] T003 Write failing contract checks in `tests/contract/test_asha_scheduling_api.py` for the Hyperband section, Name trial, Name runner, Record rung, Schedule the next trial, the task status, and `GET /api/tasks` (FR-004).

## Phase 3: User Story 1 - Name a trial and a runner (Priority: P1)

**Goal**: A named trial is stored once, a named runner is stored once, and a task holds at most 4 trials and 2 runners.

**Independent Test**: Red stays one trial and ada stays one runner after a repeated name.

- [X] T004 [US1] Add `asha_trial` and `asha_runner` to `src/task_manager/storage/schema.sql` and name them through `src/task_manager/domain/asha.py` and `src/task_manager/storage/asha_store.py` (FR-001). A task holds at most 4 trials and 2 runners. `name` is trimmed text, unique with the task.

## Phase 4: User Story 2 - Record a rung score (Priority: P2)

**Goal**: A rung score stores rung 1 or 2 and a score of 1 or 2 for one trial.

**Independent Test**: A repeated rung-score name stays score 1.

- [X] T005 [US2] Add `asha_rung` and record a rung score through the same domain and store (FR-002). A task holds at most 6 rows. `rung` is 1 or 2. `score` is 1 or 2. `task_id`, `trial_id`, and `rung` are unique together. The rung-score count is checked before the duplicate rung.

## Phase 5: User Story 3 - Schedule the next promoted trial (Priority: P3)

**Goal**: The stored promoted names are the better half of the rung 1 scores so far, and the next trial goes to the least-loaded runner.

**Independent Test**: The first schedule assigns blue to ada, and the second assigns gold to grace.

- [X] T006 [US3] Add `asha_promoted`, `asha_assignment`, and `asha_winner` and store the schedule (FR-003). `position` is 1 or greater. `trial` is unique with the task on an assignment. The winner is stored only when every promoted trial has a rung 2 score.
- [X] T007 [US3] Expose Name trial, Name runner, Record rung, and Schedule the next trial from `src/task_manager/workspace.py`, `src/task_manager/web/api.py`, and `src/task_manager/web/pages.py` (FR-003, FR-004).
- [X] T008 [US3] Show the Hyperband section in `src/task_manager/web/templates/detail.html` (FR-004).

## Phase 6: Polish

- [X] T009 Run `specs/053-asha-scheduling/quickstart.md` and confirm the existing suite stays green.

## Dependencies

T001 → T002 and T003 → T004 → T005 → T006 → T007 → T008 → T009.

## Parallel

T002 and T003 touch different files and can be written together. T004 through T008 share the domain, the store, and the page, so they stay in order.

## Notes

- Each task maps to FR-001, FR-002, FR-003, or FR-004.
- A refusal rolls back the transaction.
- No new package. No column is added to an existing table.
