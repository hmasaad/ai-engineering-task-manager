# Tasks: Online Learning and Predictive Workflow Scheduling

**Input**: Design documents from `/specs/044-online-learning/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/commands.md

**Tests**: Test-first. The checks in T002 and T003 MUST fail before T004 through T008 are implemented.

## Phase 1: Setup

- [X] T001 Confirm `specs/044-online-learning/plan.md`, `research.md`, `data-model.md`, `contracts/commands.md`, and `quickstart.md` exist.

## Phase 2: Foundational

- [X] T002 Write failing unit checks in `tests/unit/test_online_learning.py` for a length of 1 or 2, a limit of 4, a repeated name, the learned prediction, a tie, a forecast, the stored schedule, a rolled-back prediction, and another task (FR-001, FR-002, FR-003).
- [X] T003 Write failing contract checks in `tests/contract/test_online_learning_api.py` for the Learning section, Record outcome, Name forecast, Predict schedule, the start days, the task status, and `GET /api/tasks` (FR-004).

## Phase 3: User Story 1 - Record how long a kind of work took (Priority: P1)

**Goal**: A named outcome keeps a kind and a length of 1 or 2 days, and a task holds at most 4.

**Independent Test**: Past stays review took 2 after a repeated name with kind export and length 1.

- [X] T004 Add `learn_outcome` to `src/task_manager/storage/schema.sql` and record an outcome through `src/task_manager/domain/learning.py` and `src/task_manager/storage/learning_store.py` (FR-001).

## Phase 4: User Story 2 - Learn a predicted length for each kind (Priority: P2)

**Goal**: A kind predicts 2 days only when 2-day outcomes outnumber 1-day outcomes.

**Independent Test**: One 1-day review and one 2-day review still predict 1 day. A second 2-day review predicts 2 days.

- [X] T005 Count the learned prediction from stored outcomes in the same domain and store (FR-002).

## Phase 5: User Story 3 - Predict a schedule for upcoming work (Priority: P3)

**Goal**: The stored schedule runs forecasts one at a time, oldest first.

**Independent Test**: Draft starts on day 0 for 2 days, ship starts on day 2 for 1 day, and the finish day is 3.

- [X] T006 Add `learn_forecast`, `learn_plan`, and `learn_placement`, and store the predicted starts (FR-003).
- [X] T007 Expose Record outcome, Name forecast, and Predict schedule from `src/task_manager/workspace.py`, `src/task_manager/web/api.py`, and `src/task_manager/web/pages.py` (FR-003, FR-004).
- [X] T008 Show the Learning section in `src/task_manager/web/templates/detail.html` (FR-004).

## Phase 6: Polish

- [X] T009 Run `specs/044-online-learning/quickstart.md` and confirm the existing suite stays green.

## Dependencies

T001 → T002 and T003 → T004 → T005 → T006 → T007 → T008 → T009.

## Notes

- Each task maps to FR-001, FR-002, FR-003, or FR-004.
- A refusal rolls back the transaction.
- No new package. No column is added to an existing table.
