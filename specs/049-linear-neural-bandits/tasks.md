# Tasks: Contextual Bandits with Linear Models and Neural Contextual Bandits

**Input**: Design documents from `/specs/049-linear-neural-bandits/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/commands.md

**Tests**: Test-first. The checks in T002 and T003 MUST fail before T004 through T008 are implemented.

## Phase 1: Setup

- [X] T001 Confirm `specs/049-linear-neural-bandits/plan.md`, `research.md`, `data-model.md`, `contracts/commands.md`, and `quickstart.md` exist.

## Phase 2: Foundational

- [X] T002 Write failing unit checks in `tests/unit/test_linear_bandits.py` for two arms, two marked contexts, a pull, a limit of 4 pulls, a linear tie, a neural pair, a quiet choice, and a rolled-back choice (FR-001, FR-002, FR-003).
- [X] T003 Write failing contract checks in `tests/contract/test_linear_bandits_api.py` for the Models section, Name model arm, Name model context, Record model pull, Choose with model, the task status, and `GET /api/tasks` (FR-004).

## Phase 3: User Story 1 - Name an arm and a context with two marks (Priority: P1)

**Goal**: A task keeps at most 2 arms and 2 contexts, and a repeated context name does not change its marks.

**Independent Test**: Rush stays marks 1 and 1 after a repeated name with marks 0 and 0.

- [X] T004 Add `model_arm` and `model_context` to `src/task_manager/storage/schema.sql` and name them through `src/task_manager/domain/linear_bandit.py` and `src/task_manager/storage/linear_bandit_store.py` (FR-001).

## Phase 4: User Story 2 - Record a pull that changes the weights (Priority: P2)

**Goal**: A pull adds its reward only to the weights whose marks are 1.

**Independent Test**: A repeated pull name stays reward 2.

- [X] T005 Add `model_pull` and record a pull through the same domain and store (FR-002).

## Phase 5: User Story 3 - Choose an arm with a linear or neural model (Priority: P3)

**Goal**: The stored choice is the arm with the higher linear score or the higher neural score.

**Independent Test**: The linear choice in rush is ada and the neural choice in rush is grace.

- [X] T006 Add `model_choice` and store the context, the model, and the chosen arm (FR-003).
- [X] T007 Expose Name model arm, Name model context, Record model pull, and Choose with model from `src/task_manager/workspace.py`, `src/task_manager/web/api.py`, and `src/task_manager/web/pages.py` (FR-003, FR-004).
- [X] T008 Show the Models section in `src/task_manager/web/templates/detail.html` (FR-004).

## Phase 6: Polish

- [X] T009 Run `specs/049-linear-neural-bandits/quickstart.md` and confirm the existing suite stays green.

## Dependencies

T001 → T002 and T003 → T004 → T005 → T006 → T007 → T008 → T009.

## Notes

- Each task maps to FR-001, FR-002, FR-003, or FR-004.
- A refusal rolls back the transaction.
- No new package. No column is added to an existing table.
