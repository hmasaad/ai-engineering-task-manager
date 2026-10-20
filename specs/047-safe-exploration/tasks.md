# Tasks: Safe Exploration, Causal Inference, and Counterfactual Evaluation

**Input**: Design documents from `/specs/047-safe-exploration/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/commands.md

**Tests**: Test-first. The checks in T002 and T003 MUST fail before T004 through T008 are implemented.

## Phase 1: Setup

- [X] T001 Confirm `specs/047-safe-exploration/plan.md`, `research.md`, `data-model.md`, `contracts/commands.md`, and `quickstart.md` exist.

## Phase 2: Foundational

- [X] T002 Write failing unit checks in `tests/unit/test_safe_exploration.py` for a risk, a limit of 2 actions, a safe probe, a risk-2 refusal, a limit of 4 probes, an effect of 1, an effect of -1, an effect of 0, a self comparison, a rolled-back effect, and another task (FR-001, FR-002, FR-003).
- [X] T003 Write failing contract checks in `tests/contract/test_safe_exploration_api.py` for the Safety section, Name action, Record probe, Compare actions, the effect, the task status, and `GET /api/tasks` (FR-004).

## Phase 3: User Story 1 - Name an action and its risk (Priority: P1)

**Goal**: A named action keeps a risk of 1 or 2, and a task holds at most 2.

**Independent Test**: Ada stays at risk 1 after a repeated name with risk 2.

- [X] T004 Add `safe_action` to `src/task_manager/storage/schema.sql` and name an action through `src/task_manager/domain/safety.py` and `src/task_manager/storage/safety_store.py` (FR-001).

## Phase 4: User Story 2 - Explore only a safe action (Priority: P2)

**Goal**: A probe is stored only for a risk-1 action.

**Independent Test**: A probe of grace at risk 2 is refused and stores nothing.

- [X] T005 Add `safe_probe` and record a probe through the same domain and store (FR-002).

## Phase 5: User Story 3 - Compare two actions in the same state (Priority: P3)

**Goal**: The stored effect is the earliest reward of one action minus the earliest reward of the other.

**Independent Test**: Grace instead of ada in rush has effect 1.

- [X] T006 Add `safe_effect` and store the reward difference (FR-003).
- [X] T007 Expose Name action, Record probe, and Compare actions from `src/task_manager/workspace.py`, `src/task_manager/web/api.py`, and `src/task_manager/web/pages.py` (FR-003, FR-004).
- [X] T008 Show the Safety section in `src/task_manager/web/templates/detail.html` (FR-004).

## Phase 6: Polish

- [X] T009 Run `specs/047-safe-exploration/quickstart.md` and confirm the existing suite stays green.

## Dependencies

T001 → T002 and T003 → T004 → T005 → T006 → T007 → T008 → T009.

## Notes

- Each task maps to FR-001, FR-002, FR-003, or FR-004.
- A refusal rolls back the transaction.
- No new package. No column is added to an existing table.
