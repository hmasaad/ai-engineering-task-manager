# Tasks: Workflow Scheduling with Dependencies, Critical Paths, and Deadline Propagation

**Input**: Design documents from `/specs/042-critical-paths/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/commands.md

**Tests**: Test-first. The checks in T002 and T003 MUST fail before T004 through T008 are implemented.

## Phase 1: Setup

- [X] T001 Confirm `specs/042-critical-paths/plan.md`, `research.md`, `data-model.md`, `contracts/commands.md`, and `quickstart.md` exist.

## Phase 2: Foundational

- [X] T002 Write failing unit checks in `tests/unit/test_critical_paths.py` for a length of 1 or 2, a repeated name, one predecessor, a self-link, a cycle, a rolled-back link, the critical path, a tie, deadline propagation, a replaced deadline, and another task (FR-001, FR-002, FR-003).
- [X] T003 Write failing contract checks in `tests/contract/test_critical_paths_api.py` for the Workflow schedule section, Name step, Add dependency, Set deadline, the critical path, the latest times, the task status, and `GET /api/tasks` (FR-004).

## Phase 3: User Story 1 - Name a schedule step and its length (Priority: P1)

**Goal**: A named step keeps a length of 1 or 2 days.

**Independent Test**: Design stays at length 1 after a repeated name with length 2.

- [X] T004 Add `path_step` to `src/task_manager/storage/schema.sql` and name a step through `src/task_manager/domain/paths.py` and `src/task_manager/storage/path_store.py` (FR-001).

## Phase 4: User Story 2 - Record which step follows another (Priority: P2)

**Goal**: One step follows one earlier step, and a cycle is refused.

**Independent Test**: Build follows design. Design following a later step is refused and stores nothing.

- [X] T005 Add `path_link` and record a dependency through the same domain and store (FR-002).

## Phase 5: User Story 3 - Show the critical path and propagate the deadline (Priority: P3)

**Goal**: The longest chain is the critical path, and latest times count back from one deadline.

**Independent Test**: Design's latest time is `2026-12-01T00:00:00Z` and build's latest time is `2026-12-03T00:00:00Z`.

- [X] T006 Add `path_deadline` and derive the critical path and the latest times (FR-003).
- [X] T007 Expose Name step, Add dependency, and Set deadline from `src/task_manager/workspace.py`, `src/task_manager/web/api.py`, and `src/task_manager/web/pages.py` (FR-003, FR-004).
- [X] T008 Show the Workflow schedule section in `src/task_manager/web/templates/detail.html` (FR-004).

## Phase 6: Polish

- [X] T009 Run `specs/042-critical-paths/quickstart.md` and confirm the existing suite stays green.

## Dependencies

T001 → T002 and T003 → T004 → T005 → T006 → T007 → T008 → T009.

## Notes

- Each task maps to FR-001, FR-002, FR-003, or FR-004.
- A refusal rolls back the transaction.
- No new package. No column is added to an existing table.
