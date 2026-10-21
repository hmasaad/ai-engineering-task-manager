# Tasks: Multi-Armed Bandits, Thompson Sampling, and Contextual Exploration

**Input**: Design documents from `/specs/048-thompson-sampling/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/commands.md

**Tests**: Test-first. The checks in T002 and T003 MUST fail before T004 through T008 are implemented.

## Phase 1: Setup

- [X] T001 Confirm `specs/048-thompson-sampling/plan.md`, `research.md`, `data-model.md`, `contracts/commands.md`, and `quickstart.md` exist.

## Phase 2: Foundational

- [X] T002 Write failing unit checks in `tests/unit/test_thompson_sampling.py` for two arms, two contexts, a pull, a limit of 4 pulls, a middle draw, a high draw, a low draw, a tie, another context, and a rolled-back draw (FR-001, FR-002, FR-003).
- [X] T003 Write failing contract checks in `tests/contract/test_thompson_sampling_api.py` for the Exploration section, Name arm, Name context, Record pull, Draw arm, the task status, and `GET /api/tasks` (FR-004).

## Phase 3: User Story 1 - Name the arms and the contexts (Priority: P1)

**Goal**: A task keeps at most 2 arms and 2 contexts, and a repeated name does not add another.

**Independent Test**: Ada stays one arm after a repeated name. Rush stays one context after a repeated name.

- [X] T004 Add `explore_arm` and `explore_context` to `src/task_manager/storage/schema.sql` and name them through `src/task_manager/domain/exploration.py` and `src/task_manager/storage/exploration_store.py` (FR-001).

## Phase 4: User Story 2 - Record a pull in one context (Priority: P2)

**Goal**: A pull stores a win or a loss for one arm in one context.

**Independent Test**: A repeated pull name stays reward 2.

- [X] T005 Add `explore_pull` and record a pull through the same domain and store (FR-002).

## Phase 5: User Story 3 - Draw an arm from three samples (Priority: P3)

**Goal**: The stored draw is the arm with the higher middle, high, or low score in that context.

**Independent Test**: The middle draw chooses ada and the high draw chooses grace.

- [X] T006 Add `explore_draw` and store the chosen arm and sample name (FR-003).
- [X] T007 Expose Name arm, Name context, Record pull, and Draw arm from `src/task_manager/workspace.py`, `src/task_manager/web/api.py`, and `src/task_manager/web/pages.py` (FR-003, FR-004).
- [X] T008 Show the Exploration section in `src/task_manager/web/templates/detail.html` (FR-004).

## Phase 6: Polish

- [X] T009 Run `specs/048-thompson-sampling/quickstart.md` and confirm the existing suite stays green.

## Dependencies

T001 → T002 and T003 → T004 → T005 → T006 → T007 → T008 → T009.

## Notes

- Each task maps to FR-001, FR-002, FR-003, or FR-004.
- A refusal rolls back the transaction.
- No new package. No column is added to an existing table.
