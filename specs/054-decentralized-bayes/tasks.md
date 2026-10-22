# Tasks: Distributed Bayesian Optimization and Decentralized Scheduling

**Input**: Design documents from `/specs/054-decentralized-bayes/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/commands.md

**Tests**: Test-first. The checks in T002 and T003 MUST fail before T004 through T008 are implemented.

## Phase 1: Setup

- [X] T001 Confirm `specs/054-decentralized-bayes/plan.md`, `research.md`, `data-model.md`, `contracts/commands.md`, and `quickstart.md` exist.

## Phase 2: Foundational

- [X] T002 Write failing unit checks in `tests/unit/test_decentralized_bayes.py` for four points, two nodes, a report, local suggestions, the agreement, and a rolled-back report (FR-001, FR-002, FR-003).
- [X] T003 Write failing contract checks in `tests/contract/test_decentralized_bayes_api.py` for the Consensus section, Name point, Name node, Record report, Agree on a design, the task status, and `GET /api/tasks` (FR-004).

## Phase 3: User Story 1 - Name a point and a node (Priority: P1)

**Goal**: A named point is stored once, a named node is stored once, and a task holds at most 4 points and 2 nodes.

**Independent Test**: Ada stays one point with setting 1, and north stays one node, after a repeated name.

- [X] T004 [US1] Add `consensus_point` and `consensus_node` to `src/task_manager/storage/schema.sql` and name them through `src/task_manager/domain/consensus.py` and `src/task_manager/storage/consensus_store.py` (FR-001). A task holds at most 4 points and 2 nodes. `name` is trimmed text, unique with the task. `setting` is 1 or 2.

## Phase 4: User Story 2 - Record a local report (Priority: P2)

**Goal**: A report stores one node's score of 1 or 2 for one point.

**Independent Test**: A repeated report name stays score 2.

- [X] T005 [US2] Add `consensus_report` and record a report through the same domain and store (FR-002). A task holds at most 4 rows. `score` is 1 or 2. `task_id`, `node_id`, and `point_id` are unique together. The report count is checked before the duplicate pair.

## Phase 5: User Story 3 - Agree on the next point (Priority: P3)

**Goal**: Each node suggests one unreported point, and the agreement is the point suggested by the most nodes.

**Independent Test**: North and south both suggest mina, and the agreement is mina on north with 2 suggestions.

- [X] T006 [US3] Add `consensus_proposal` and `consensus_choice` and store the agreement (FR-003). `position` is 1 or greater. `suggestions` is 1 or 2. The choice names the point suggested by the most nodes and the earliest node that suggested it.
- [X] T007 [US3] Expose Name point, Name node, Record report, and Agree on a design from `src/task_manager/workspace.py`, `src/task_manager/web/api.py`, and `src/task_manager/web/pages.py` (FR-003, FR-004).
- [X] T008 [US3] Show the Consensus section in `src/task_manager/web/templates/detail.html` (FR-004).

## Phase 6: Polish

- [X] T009 Run `specs/054-decentralized-bayes/quickstart.md` and confirm the existing suite stays green.

## Dependencies

T001 → T002 and T003 → T004 → T005 → T006 → T007 → T008 → T009.

## Parallel

T002 and T003 touch different files and can be written together. T004 through T008 share the domain, the store, and the page, so they stay in order.

## Notes

- Each task maps to FR-001, FR-002, FR-003, or FR-004.
- A refusal rolls back the transaction.
- No new package. No column is added to an existing table.
