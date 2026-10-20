---
description: "Task list for Deadline-Aware Scheduling and Service-Level Objectives (SLOs)"
---

# Tasks: Deadline-Aware Scheduling and Service-Level Objectives (SLOs)

**Input**: Design documents from `/specs/041-deadline-slos/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Included. The spec says the rules are covered by automated checks. Constitution Principle II requires a failing test before the behavior exists.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested on its own.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Single project: `src/task_manager/`, `tests/` at the repository root

## Phase 1: Setup

**Purpose**: The objective and service tables. No existing table is altered.

- [X] T001 Add `slo_objective` and `slo_service` in `src/task_manager/storage/schema.sql` with `CREATE TABLE IF NOT EXISTS` only, as in `specs/041-deadline-slos/data-model.md`. `UNIQUE (task_id, name)` on each table. `slo_service.result` is `met` or `missed`. `slo_objective.deadline` is text with length greater than 0.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Objectives and services can be stored and read oldest first.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T002 Read and insert objectives and services in `src/task_manager/storage/slo_store.py`. A second insert for the same task and name does not add a row. Return waiting objectives and services oldest first.

**Checkpoint**: An objective can be stored without a service.

---

## Phase 3: User Story 1 - Name an objective and its deadline (Priority: P1) 🎯 MVP

**Goal**: A named objective keeps the deadline the engineer gave.

**Independent Test**: Set " export " due `2026-12-01T00:00:00Z`. Set "export" due `2026-01-01T00:00:00Z` again. Export stays due `2026-12-01T00:00:00Z`.

### Tests for User Story 1

- [X] T003 [P] [US1] Add the deadline checks in `tests/unit/test_deadline_slos.py`. Confirm they fail before the behavior exists.

### Implementation for User Story 1

- [X] T004 [US1] Set an objective in `src/task_manager/domain/slo.py`. Pass the command through `src/task_manager/workspace.py`. Include `slo` on the task detail from `src/task_manager/storage/task_store.py`. Accept only a real UTC time in the form `2026-12-01T00:00:00Z`.

**Checkpoint**: A second use of the same name changes no deadline.

---

## Phase 4: User Story 2 - Serve the earliest deadline and record the objective (Priority: P2)

**Goal**: A named service goes to the earliest deadline and records met or missed.

**Independent Test**: Rush due `2026-10-01T00:00:00Z` is served as missed. Export due `2026-12-01T00:00:00Z` is served as met.

### Tests for User Story 2

- [X] T005 [P] [US2] Extend `tests/unit/test_deadline_slos.py` for an earliest deadline, a tie, a repeated service, a missing objective, and a rolled-back service.

### Implementation for User Story 2

- [X] T006 [US2] Serve one objective in `src/task_manager/domain/slo.py`. Use the sentences in `specs/041-deadline-slos/contracts/commands.md`. The service and its met or missed result commit together. A Refusal leaves no row.

**Checkpoint**: Equal deadlines choose the objective stored first.

---

## Phase 5: User Story 3 - Keep a later deadline from jumping the queue (Priority: P3)

**Goal**: A served objective is skipped, and a finished schedule refuses the next service. The page shows the objectives.

**Independent Test**: After both objectives are served, "three" is refused with `Every objective has been served.` The page shows `one missed rush`.

### Tests for User Story 3

- [X] T007 [P] [US3] Extend `tests/unit/test_deadline_slos.py` for a finished schedule, a blank service, and another task. Add `tests/contract/test_deadline_slos_api.py` for the page and the two commands.

### Implementation for User Story 3

- [X] T008 [US3] Refuse a service when every objective has been served in `src/task_manager/domain/slo.py`. Show the objectives in `src/task_manager/web/templates/detail.html`. Accept the commands in `src/task_manager/web/api.py` and `src/task_manager/web/pages.py`.

**Checkpoint**: The page and the command agree on which objective was served and whether it was met.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T009 Run the checks in `specs/041-deadline-slos/quickstart.md` and confirm the existing suite stays green.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on T001. Blocks the stories.
- **User Story 1 (Phase 3)**: Depends on Phase 2.
- **User Story 2 (Phase 4)**: Depends on User Story 1, because a service needs an objective.
- **User Story 3 (Phase 5)**: Depends on User Story 2, because the page shows a service.
- **Polish (Phase 6)**: Depends on the stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Independently testable by setting two objectives.
- **User Story 2 (P2)**: Independently testable once an objective can be set.
- **User Story 3 (P3)**: Independently testable once a service can be recorded.

### Parallel Opportunities

- T003 can be written while T002 is reviewed, and it fails until T004.
- T005 and T007 touch the same test file, so they stay sequential.

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete User Story 1 and confirm each objective keeps its deadline.
3. Add the earliest-deadline service, then the finished-schedule refusal and the page.

### Incremental Delivery

1. Setup and store methods.
2. User Story 1: set an objective.
3. User Story 2: serve the earliest deadline and record met or missed.
4. User Story 3: refuse a finished schedule and show the page.
5. The full pytest suite.
