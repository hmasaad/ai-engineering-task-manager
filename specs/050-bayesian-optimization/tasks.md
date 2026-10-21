# Tasks: Constrained and Multi-Objective Bayesian Optimization

**Input**: Design documents from `/specs/050-bayesian-optimization/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/commands.md

**Tests**: Test-first. The checks in T002 and T003 MUST fail before T004 through T008 are implemented.

## Phase 1: Setup

- [X] T001 Confirm `specs/050-bayesian-optimization/plan.md`, `research.md`, `data-model.md`, `contracts/commands.md`, and `quickstart.md` exist.

## Phase 2: Foundational

- [X] T002 Write failing unit checks in `tests/unit/test_bayesian_optimization.py` for four designs, an observation, a violated design, a dominated front, a tradeoff front, the next design, and a rolled-back recommendation (FR-001, FR-002, FR-003).
- [X] T003 Write failing contract checks in `tests/contract/test_bayesian_optimization_api.py` for the Search section, Name design, Record observation, Recommend a design, the task status, and `GET /api/tasks` (FR-004).

## Phase 3: User Story 1 - Name a design and its two settings (Priority: P1)

**Goal**: A named design keeps two settings, and a task holds at most 4.

**Independent Test**: Ada stays at settings 1 and 1 after a repeated name with settings 2 and 2.

- [X] T004 Add `bayes_design` to `src/task_manager/storage/schema.sql` and name a design through `src/task_manager/domain/bayes.py` and `src/task_manager/storage/bayes_store.py` (FR-001).

## Phase 4: User Story 2 - Record two objectives and a constraint (Priority: P2)

**Goal**: An observation stores two objective scores and a constraint for one design.

**Independent Test**: A repeated observation name stays constraint 1.

- [X] T005 Add `bayes_observation` and record an observation through the same domain and store (FR-002).

## Phase 5: User Story 3 - Recommend the next feasible design (Priority: P3)

**Goal**: The stored front omits violated and dominated observations, and the next design has the highest neighbor score.

**Independent Test**: The front is ada and the next design is mina.

- [X] T006 Add `bayes_pick` and `bayes_front` and store the recommendation (FR-003).
- [X] T007 Expose Name design, Record observation, and Recommend a design from `src/task_manager/workspace.py`, `src/task_manager/web/api.py`, and `src/task_manager/web/pages.py` (FR-003, FR-004).
- [X] T008 Show the Search section in `src/task_manager/web/templates/detail.html` (FR-004).

## Phase 6: Polish

- [X] T009 Run `specs/050-bayesian-optimization/quickstart.md` and confirm the existing suite stays green.

## Dependencies

T001 → T002 and T003 → T004 → T005 → T006 → T007 → T008 → T009.

## Notes

- Each task maps to FR-001, FR-002, FR-003, or FR-004.
- A refusal rolls back the transaction.
- No new package. No column is added to an existing table.
