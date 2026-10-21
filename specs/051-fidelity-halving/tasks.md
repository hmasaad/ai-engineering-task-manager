# Tasks: Multi-Fidelity Bayesian Optimization and Successive Halving

**Input**: Design documents from `/specs/051-fidelity-halving/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/commands.md

**Tests**: Test-first. The checks in T002 and T003 MUST fail before T004 through T008 are implemented.

## Phase 1: Setup

- [X] T001 Confirm `specs/051-fidelity-halving/plan.md`, `research.md`, `data-model.md`, `contracts/commands.md`, and `quickstart.md` exist.

## Phase 2: Foundational

- [X] T002 Write failing unit checks in `tests/unit/test_fidelity_halving.py` for four candidates, a cheap measurement, the kept half, an expensive winner, a tie, and a rolled-back measurement (FR-001, FR-002, FR-003).
- [X] T003 Write failing contract checks in `tests/contract/test_fidelity_halving_api.py` for the Fidelity section, Name candidate, Record fidelity, Halve the field, the task status, and `GET /api/tasks` (FR-004).

## Phase 3: User Story 1 - Name a candidate (Priority: P1)

**Goal**: A named candidate is stored once, and a task holds at most 4.

**Independent Test**: Ada stays one candidate after a repeated name.

- [X] T004 [US1] Add `fidelity_candidate` to `src/task_manager/storage/schema.sql` and name a candidate through `src/task_manager/domain/fidelity.py` and `src/task_manager/storage/fidelity_store.py` (FR-001). A task holds at most 4 rows. `name` is trimmed text, unique with the task.

## Phase 4: User Story 2 - Record a cheap or expensive measurement (Priority: P2)

**Goal**: A measurement stores fidelity 1 or 2 and a score of 1 or 2 for one candidate.

**Independent Test**: A repeated measurement name stays score 2.

- [X] T005 [US2] Add `fidelity_measurement` and record a measurement through the same domain and store (FR-002). A task holds at most 6 rows. `fidelity` is 1 or 2. `score` is 1 or 2. `task_id`, `candidate_id`, and `fidelity` are unique together. The measurement count is checked before the duplicate fidelity.

## Phase 5: User Story 3 - Halve the field and name the winner (Priority: P3)

**Goal**: The stored kept names are the better half of the cheap scores, and the winner has the highest expensive score.

**Independent Test**: The kept names are grace and mina, and the winner is mina.

- [X] T006 [US3] Add `fidelity_round` and `fidelity_kept` and store the halving (FR-003). `winner` is the trimmed candidate name or empty. `position` is 1 or greater, in the order the half was chosen.
- [X] T007 [US3] Expose Name candidate, Record fidelity, and Halve the field from `src/task_manager/workspace.py`, `src/task_manager/web/api.py`, and `src/task_manager/web/pages.py` (FR-003, FR-004).
- [X] T008 [US3] Show the Fidelity section in `src/task_manager/web/templates/detail.html` (FR-004).

## Phase 6: Polish

- [X] T009 Run `specs/051-fidelity-halving/quickstart.md` and confirm the existing suite stays green.

## Dependencies

T001 → T002 and T003 → T004 → T005 → T006 → T007 → T008 → T009.

## Parallel

T002 and T003 touch different files and can be written together. T004 through T008 share the domain, the store, and the page, so they stay in order.

## Notes

- Each task maps to FR-001, FR-002, FR-003, or FR-004.
- A refusal rolls back the transaction.
- No new package. No column is added to an existing table.
