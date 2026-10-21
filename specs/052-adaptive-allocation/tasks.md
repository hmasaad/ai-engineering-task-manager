# Tasks: Adaptive Resource Allocation for Workflow and Agent Optimization

**Input**: Design documents from `/specs/052-adaptive-allocation/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/commands.md

**Tests**: Test-first. The checks in T002 and T003 MUST fail before T004 through T008 are implemented.

## Phase 1: Setup

- [X] T001 Confirm `specs/052-adaptive-allocation/plan.md`, `research.md`, `data-model.md`, `contracts/commands.md`, and `quickstart.md` exist.

## Phase 2: Foundational

- [X] T002 Write failing unit checks in `tests/unit/test_adaptive_allocation.py` for four agents, a yield, shares of 3 and 1, an equal split, a share of 0, and a rolled-back yield (FR-001, FR-002, FR-003).
- [X] T003 Write failing contract checks in `tests/contract/test_adaptive_allocation_api.py` for the Allocation section, Name agent, Record yield, Allocate the pool, the task status, and `GET /api/tasks` (FR-004).

## Phase 3: User Story 1 - Name an agent (Priority: P1)

**Goal**: A named agent is stored once, and a task holds at most 4.

**Independent Test**: Ada stays one agent after a repeated name.

- [X] T004 [US1] Add `allocation_agent` to `src/task_manager/storage/schema.sql` and name an agent through `src/task_manager/domain/allocation.py` and `src/task_manager/storage/allocation_store.py` (FR-001). A task holds at most 4 rows. `name` is trimmed text, unique with the task.

## Phase 4: User Story 2 - Record a yield (Priority: P2)

**Goal**: A yield stores a value of 1 or 2 for one agent.

**Independent Test**: A repeated yield name stays value 2.

- [X] T005 [US2] Add `allocation_yield` and record a yield through the same domain and store (FR-002). A task holds at most 4 rows. `value` is 1 or 2. `task_id` and `agent_id` are unique together. The yield count is checked before the duplicate agent.

## Phase 5: User Story 3 - Allocate the workflow budget (Priority: P3)

**Goal**: The stored shares add up to 4, and each unit goes to the agent with the larger product.

**Independent Test**: Ada receives 3 units and grace receives 1.

- [X] T006 [US3] Add `allocation_share` and store the allocation (FR-003). `units` is a whole number from 0 through 4. `position` is 1 or greater, in agent order. The units for a task add up to 4.
- [X] T007 [US3] Expose Name agent, Record yield, and Allocate the pool from `src/task_manager/workspace.py`, `src/task_manager/web/api.py`, and `src/task_manager/web/pages.py` (FR-003, FR-004).
- [X] T008 [US3] Show the Allocation section in `src/task_manager/web/templates/detail.html` (FR-004).

## Phase 6: Polish

- [X] T009 Run `specs/052-adaptive-allocation/quickstart.md` and confirm the existing suite stays green.

## Dependencies

T001 → T002 and T003 → T004 → T005 → T006 → T007 → T008 → T009.

## Parallel

T002 and T003 touch different files and can be written together. T004 through T008 share the domain, the store, and the page, so they stay in order.

## Notes

- Each task maps to FR-001, FR-002, FR-003, or FR-004.
- A refusal rolls back the transaction.
- No new package. No column is added to an existing table.
