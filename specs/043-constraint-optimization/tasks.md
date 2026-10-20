# Tasks: Constraint Programming and Optimization for Workflow Scheduling

**Input**: Design documents from `/specs/043-constraint-optimization/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/commands.md

**Tests**: Test-first. The checks in T002 and T003 MUST fail before T004 through T008 are implemented.

## Phase 1: Setup

- [X] T001 Confirm `specs/043-constraint-optimization/plan.md`, `research.md`, `data-model.md`, `contracts/commands.md`, and `quickstart.md` exist.

## Phase 2: Foundational

- [X] T002 Write failing unit checks in `tests/unit/test_constraint_optimization.py` for a length of 1 or 2, a limit of 4, a repeated name, precedence, a cycle, a cleared plan, capacity, the earliest finish day, a tie, a rolled-back optimization, and another task (FR-001, FR-002, FR-003).
- [X] T003 Write failing contract checks in `tests/contract/test_constraint_optimization_api.py` for the Optimization section, Name activity, Add constraint, Set capacity, Optimize schedule, the start days, the task status, and `GET /api/tasks` (FR-004).

## Phase 3: User Story 1 - Name an activity and its length (Priority: P1)

**Goal**: A named activity keeps a length of 1 or 2 days, and a task holds at most 4.

**Independent Test**: Design stays at length 1 after a repeated name with length 2.

- [X] T004 Add `opt_activity` to `src/task_manager/storage/schema.sql` and name an activity through `src/task_manager/domain/optimization.py` and `src/task_manager/storage/optimization_store.py` (FR-001).

## Phase 4: User Story 2 - Record a precedence constraint (Priority: P2)

**Goal**: One activity can wait for several earlier activities, and a cycle is refused.

**Independent Test**: Test starts after build. Build starting after test is refused and stores nothing.

- [X] T005 Add `opt_constraint` and record a precedence through the same domain and store (FR-002).

## Phase 5: User Story 3 - Optimize the schedule under a capacity (Priority: P3)

**Goal**: The stored plan finishes on the earliest legal day.

**Independent Test**: With capacity 2, design and build start on day 0, test starts on day 2, and the finish day is 3.

- [X] T006 Add `opt_capacity`, `opt_plan`, and `opt_placement`, and store the optimized starts (FR-003).
- [X] T007 Expose Name activity, Add constraint, Set capacity, and Optimize schedule from `src/task_manager/workspace.py`, `src/task_manager/web/api.py`, and `src/task_manager/web/pages.py` (FR-003, FR-004).
- [X] T008 Show the Optimization section in `src/task_manager/web/templates/detail.html` (FR-004).

## Phase 6: Polish

- [X] T009 Run `specs/043-constraint-optimization/quickstart.md` and confirm the existing suite stays green.

## Dependencies

T001 → T002 and T003 → T004 → T005 → T006 → T007 → T008 → T009.

## Notes

- Each task maps to FR-001, FR-002, FR-003, or FR-004.
- A refusal rolls back the transaction.
- No new package. No column is added to an existing table.
