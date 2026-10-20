# Tasks: Contextual Bandits and Reinforcement Learning for Workflow Scheduling

**Input**: Design documents from `/specs/045-contextual-bandits/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/commands.md

**Tests**: Test-first. The checks in T002 and T003 MUST fail before T004 through T008 are implemented.

## Phase 1: Setup

- [X] T001 Confirm `specs/045-contextual-bandits/plan.md`, `research.md`, `data-model.md`, `contracts/commands.md`, and `quickstart.md` exist.

## Phase 2: Foundational

- [X] T002 Write failing unit checks in `tests/unit/test_contextual_bandits.py` for two actions, four contexts, a reward, a repeated name, the learned total, an untried action, an equal average, a higher average, another context, a rolled-back choice, and another task (FR-001, FR-002, FR-003).
- [X] T003 Write failing contract checks in `tests/contract/test_contextual_bandits_api.py` for the Bandit section, Name action, Name context, Record trial, Choose action, the learned totals, the task status, and `GET /api/tasks` (FR-004).

## Phase 3: User Story 1 - Name the actions and the contexts (Priority: P1)

**Goal**: A named action and a named context stay as given, with at most 2 actions and 4 contexts.

**Independent Test**: Ada stays one action after a repeated name. Rush stays one context after a repeated name.

- [X] T004 Add `bandit_action` and `bandit_context` to `src/task_manager/storage/schema.sql` and name them through `src/task_manager/domain/bandit.py` and `src/task_manager/storage/bandit_store.py` (FR-001).

## Phase 4: User Story 2 - Record a reward for an action in a context (Priority: P2)

**Goal**: A trial keeps its reward, and each pair shows its total and its count.

**Independent Test**: One trial of reward 1 stays reward 1 and shows a total of 1 from 1 trial.

- [X] T005 Add `bandit_trial` and record a reward through the same domain and store (FR-002).

## Phase 5: User Story 3 - Choose the action for a context (Priority: P3)

**Goal**: The stored choice tries an untried action, then takes the higher average.

**Independent Test**: Equal averages choose ada. After grace has a total of 3 from 2 trials, the choice is grace.

- [X] T006 Add `bandit_choice` and store the chosen action (FR-003).
- [X] T007 Expose Name action, Name context, Record trial, and Choose action from `src/task_manager/workspace.py`, `src/task_manager/web/api.py`, and `src/task_manager/web/pages.py` (FR-003, FR-004).
- [X] T008 Show the Bandit section in `src/task_manager/web/templates/detail.html` (FR-004).

## Phase 6: Polish

- [X] T009 Run `specs/045-contextual-bandits/quickstart.md` and confirm the existing suite stays green.

## Dependencies

T001 → T002 and T003 → T004 → T005 → T006 → T007 → T008 → T009.

## Notes

- Each task maps to FR-001, FR-002, FR-003, or FR-004.
- A refusal rolls back the transaction.
- No new package. No column is added to an existing table.
