---
description: "Task list for Task Dependencies"
---

# Tasks: Task Dependencies

**Input**: Design documents from `/specs/019-task-dependencies/`

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

**Purpose**: The link table. `task` is not altered.

- [X] T001 Add `task_dependency` to `src/task_manager/storage/schema.sql` with `CREATE TABLE IF NOT EXISTS` only. `task_id` and `prerequisite_id` are the primary key, both reference `task(id)`, and a check requires them to differ. Add `idx_task_dependency_prerequisite` on `prerequisite_id`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: A task can be read with its prerequisites before the commands exist.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T002 Add `src/task_manager/storage/dependency_store.py` to insert one link, delete one link, list a task's prerequisites by id as `id`, `title`, and `status`, and read every task and every link. In `src/task_manager/storage/task_store.py`, add `prerequisites` and `blocked_by` to the task detail. `blocked_by` is null when no prerequisite is unfinished.

**Checkpoint**: A task with no prerequisite reads `prerequisites` as `[]` and `blocked_by` as null.

---

## Phase 3: User Story 1 - Record a prerequisite (Priority: P1) 🎯 MVP

**Goal**: The engineer names one prerequisite. Self-links, unknown tasks, and cycles are refused. A repeated name stays one link. The engineer can remove a link.

**Independent Test**: Link "Add export" to "Write the label". The task lists it once. A self-link, an unknown task, and a cycle store nothing.

### Tests for User Story 1 ⚠️

- [X] T003 [P] [US1] Add failing unit tests in `tests/unit/test_dependency.py` for a stored prerequisite, a repeated link, a self-link `A task cannot depend on itself.`, an unknown prerequisite `Prerequisite not found.`, a three-task cycle `That dependency would form a cycle.`, removal, and a cancelled task `A cancelled task cannot be changed. Continued work is a new task.` Opening the task does not add a second link. Neither status changes.

- [X] T004 [P] [US1] Add failing contract tests in `tests/contract/test_dependency_api.py` for `POST /api/tasks/{id}/prerequisites` and removal. A missing `prerequisite_id` is 400 `The request is missing a required field or has the wrong shape.` A blank page value is `Name the prerequisite task.`

### Implementation for User Story 1

- [X] T005 [US1] Implement add and remove in `src/task_manager/domain/dependency.py`. Check the task, a cancelled task, a blank id, the prerequisite, a self-link, and a cycle, in that order. Insert only when the link is new. Wire `src/task_manager/workspace.py`, `src/task_manager/web/api.py`, `src/task_manager/web/pages.py`, and the form and list in `src/task_manager/web/templates/detail.html`. Field id `prerequisite-id`. Button `Add prerequisite`. Button `Remove prerequisite`.

**Checkpoint**: User Story 1 works. A subtask link does not create a prerequisite.

---

## Phase 4: User Story 2 - Show a valid execution order (Priority: P2)

**Goal**: One reading lists every task with each prerequisite first and the lower id first when several tasks could be next.

**Independent Test**: "Add export" depends on "Write the label", which depends on "Choose the format". The order is format, label, then export.

### Tests for User Story 2 ⚠️

- [X] T006 [P] [US2] Add failing unit and contract coverage for `GET /api/execution-order` in `tests/unit/test_dependency.py` and `tests/contract/test_dependency_api.py`. A second read does not change a status. `GET /api/tasks` stays the top-level list.

### Implementation for User Story 2

- [X] T007 [US2] Implement the order in `src/task_manager/domain/dependency.py` and `src/task_manager/workspace.py`. Add `GET /api/execution-order` in `src/task_manager/web/api.py` and the `Execution order` section in `src/task_manager/web/templates/list.html` through `src/task_manager/web/pages.py`. Show the section only when the list is not empty.

**Checkpoint**: User Stories 1 and 2 both work. Reading the order writes nothing.

---

## Phase 5: User Story 3 - Hold the start while a prerequisite is unfinished (Priority: P3)

**Goal**: A Ready task cannot be started while a prerequisite is not Completed. The refusal names incomplete or unverified. An In Progress task stays In Progress when a prerequisite is reopened.

**Independent Test**: Start "Add export" while "Write the label" is Draft. The refusal names "Write the label" and "Add export" stays Ready. After "Write the label" is Completed, "Add export" starts.

### Tests for User Story 3 ⚠️

- [X] T008 [US3] Add failing tests in `tests/unit/test_dependency.py` and `tests/contract/test_dependency_api.py` for `Blocked by Write the label (Draft): incomplete.`, the unverified form, two prerequisites in id order, a Draft task that still returns `The task must be Ready to start work.`, a Completed prerequisite that allows start, and an In Progress task that stays In Progress when a prerequisite is reopened. Marking Ready stays available while a prerequisite is unfinished.

### Implementation for User Story 3

- [X] T009 [US3] In `src/task_manager/domain/status.py`, after the Ready check, refuse start with the blocked sentence from `src/task_manager/domain/dependency.py`. Show `blocked_by` under Status in `src/task_manager/web/templates/detail.html`. Do not change complete or cancel.

**Checkpoint**: All three stories work. Existing start, complete, and cancel rules stay for a task with no prerequisite.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T010 Run the full pytest suite.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup
- **User Story 1 (Phase 3)**: Depends on Foundational
- **User Story 2 (Phase 4)**: Depends on Foundational and on stored links from User Story 1
- **User Story 3 (Phase 5)**: Depends on User Story 1
- **Polish (Phase 6)**: Depends on all stories

### User Story Dependencies

- **User Story 1 (P1)**: First, because the order and the hold read its links
- **User Story 2 (P2)**: After User Story 1. Independently testable by reading the order
- **User Story 3 (P3)**: After User Story 1. Independently testable by starting a Ready task

### Parallel Opportunities

- T003 and T004 can run in parallel
- T006 can be written with T003 once the link command exists

---

## Parallel Example: User Story 1

```bash
Task: "Unit tests in tests/unit/test_dependency.py"
Task: "Contract tests in tests/contract/test_dependency_api.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2
2. Complete User Story 1
3. Stop and validate a stored prerequisite and a refused cycle

### Incremental Delivery

1. User Story 1 stores a valid link
2. User Story 2 shows the order
3. User Story 3 holds start and names the unfinished prerequisite

---

## Notes

- [P] tasks = different files, no dependencies
- Do not redefine Ready
- Do not treat a subtask as a prerequisite
- Do not wrap `GET /api/tasks` in a new object
