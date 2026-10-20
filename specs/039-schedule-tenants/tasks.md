---
description: "Task list for Multi-Tenant Workflow Scheduling, Fairness, and Resource Quotas"
---

# Tasks: Multi-Tenant Workflow Scheduling, Fairness, and Resource Quotas

**Input**: Design documents from `/specs/039-schedule-tenants/`

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

**Purpose**: The tenant and turn tables. No existing table is altered.

- [X] T001 Add `schedule_tenant` and `schedule_turn` in `src/task_manager/storage/schema.sql` with `CREATE TABLE IF NOT EXISTS` only, as in `specs/039-schedule-tenants/data-model.md`. `UNIQUE (task_id, name)` on each table. `schedule_tenant.quota` is an integer greater than 0.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Tenants and turns can be stored and read oldest first.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T002 Read and insert tenants and turns in `src/task_manager/storage/schedule_store.py`. A second insert for the same task and name does not add a row. Return tenants and turns oldest first.

**Checkpoint**: A tenant can be stored without a turn.

---

## Phase 3: User Story 1 - Admit a tenant under a quota (Priority: P1) 🎯 MVP

**Goal**: A named tenant starts at 0 of 2.

**Independent Test**: Admit " ada " and "grace". Both are at 0 of 2. Admit "ada" again. The task still has two tenants.

### Tests for User Story 1

- [X] T003 [P] [US1] Add the admission checks in `tests/unit/test_schedule_tenants.py`. Confirm they fail before the behavior exists.

### Implementation for User Story 1

- [X] T004 [US1] Admit a tenant in `src/task_manager/domain/schedule.py`. Pass the command through `src/task_manager/workspace.py`. Include `schedule` on the task detail from `src/task_manager/storage/task_store.py`. The quota is 2. Turns used are the stored turns for that tenant.

**Checkpoint**: A second admission of the same name adds no tenant.

---

## Phase 4: User Story 2 - Grant the next turn to the least-used tenant (Priority: P2)

**Goal**: A named turn goes to the tenant with the fewest turns. The tenant admitted first wins a tie.

**Independent Test**: Ada receives "one" and "three". Grace receives "two" and "four".

### Tests for User Story 2

- [X] T005 [P] [US2] Extend `tests/unit/test_schedule_tenants.py` for a fair grant, a repeated turn, a missing tenant, and a rolled-back turn.

### Implementation for User Story 2

- [X] T006 [US2] Grant one turn in `src/task_manager/domain/schedule.py`. Use the sentences in `specs/039-schedule-tenants/contracts/commands.md`. The turn and the tenant who receives it commit together. A Refusal leaves no row.

**Checkpoint**: Equal used counts choose the tenant stored first.

---

## Phase 5: User Story 3 - Stop a tenant who has used the quota (Priority: P3)

**Goal**: A tenant at two turns is skipped, and a full schedule refuses the next turn. The page shows the schedule.

**Independent Test**: After four turns, "five" is refused with `Every tenant is at its quota.` The page shows `ada: 2 of 2` and `one granted to ada`.

### Tests for User Story 3

- [X] T007 [P] [US3] Extend `tests/unit/test_schedule_tenants.py` for a tenant at the quota, a full schedule, a blank turn, and another task. Add `tests/contract/test_schedule_tenants_api.py` for the page and the two commands.

### Implementation for User Story 3

- [X] T008 [US3] Skip a tenant at quota 2 in `src/task_manager/domain/schedule.py`. Show the schedule in `src/task_manager/web/templates/detail.html`. Accept the commands in `src/task_manager/web/api.py` and `src/task_manager/web/pages.py`.

**Checkpoint**: The page and the command agree on who received the turn.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T009 Run the checks in `specs/039-schedule-tenants/quickstart.md` and confirm the existing suite stays green.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on T001. Blocks the stories.
- **User Story 1 (Phase 3)**: Depends on Phase 2.
- **User Story 2 (Phase 4)**: Depends on User Story 1, because a turn needs a tenant.
- **User Story 3 (Phase 5)**: Depends on User Story 2, because the page shows a granted turn.
- **Polish (Phase 6)**: Depends on the stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Independently testable by admitting two tenants.
- **User Story 2 (P2)**: Independently testable once a tenant can be admitted.
- **User Story 3 (P3)**: Independently testable once a turn can be granted.

### Parallel Opportunities

- T003 can be written while T002 is reviewed, and it fails until T004.
- T005 and T007 touch the same test file, so they stay sequential.

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete User Story 1 and confirm each tenant starts at 0 of 2.
3. Add the fair grant, then the quota refusal and the page.

### Incremental Delivery

1. Setup and store methods.
2. User Story 1: admit a tenant.
3. User Story 2: grant a turn fairly.
4. User Story 3: enforce the quota and show the page.
5. The full pytest suite.
