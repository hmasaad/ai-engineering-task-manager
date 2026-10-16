---
description: "Task list for Workflow Replay and Deterministic Execution"
---

# Tasks: Workflow Replay and Deterministic Execution

**Input**: Design documents from `/specs/026-deterministic-replay/`

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

**Purpose**: Confirm the report can be derived from stored rows. No table is added.

- [X] T001 Confirm `src/task_manager/storage/schema.sql` is unchanged. The report in `specs/026-deterministic-replay/data-model.md` is derived from the current version, file reads, and folder changes.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: One read-only computation shared by the command and the task page.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T002 Add the report computation in `src/task_manager/domain/workflow.py` and expose it from `src/task_manager/workspace.py` without calling the clock.

**Checkpoint**: A second call returns the same report and writes nothing.

---

## Phase 3: User Story 1 - Replay a finished workflow from its record (Priority: P1) 🎯 MVP

**Goal**: Completed steps match their stored effects, and a repeated replay is identical.

**Independent Test**: Complete two reads, replay twice, and see one read of each file.

### Tests for User Story 1

- [X] T003 [P] [US1] Add the finished-workflow and missing-effect checks in `tests/unit/test_deterministic_replay.py`. Confirm they fail before the behavior exists.

### Implementation for User Story 1

- [X] T004 [US1] Match each completed read or folder to its stored effect in `src/task_manager/domain/workflow.py`. Stop with `Stopped at {title}: the stored effect is missing.` when the effect is absent.

**Checkpoint**: A repeated replay does not read a file again.

---

## Phase 4: User Story 2 - Stop at the first step that has not finished (Priority: P2)

**Goal**: Pending, waiting, and failed steps stop the report without being performed.

**Independent Test**: Leave the second step pending. The report matches the first step and does not read the second file.

### Tests for User Story 2

- [X] T005 [P] [US2] Extend `tests/unit/test_deterministic_replay.py` for a pending step, a waiting folder, a failed step, and a running step.

### Implementation for User Story 2

- [X] T006 [US2] Stop the walk in `src/task_manager/domain/workflow.py` with the sentences in `specs/026-deterministic-replay/contracts/commands.md`.

**Checkpoint**: A waiting change is not approved by replay.

---

## Phase 5: User Story 3 - Show the report on the task (Priority: P3)

**Goal**: The task page shows the report, and Replay execution shows it again.

**Independent Test**: The page contains the matched file, the stop sentence, and Replay execution.

### Tests for User Story 3

- [X] T007 [P] [US3] Add `tests/contract/test_deterministic_replay_api.py` for the page and `POST /api/tasks/{id}/workflow/replay-execution`.

### Implementation for User Story 3

- [X] T008 [US3] Show the report in `src/task_manager/web/templates/detail.html` and accept the command in `src/task_manager/web/api.py` and `src/task_manager/web/pages.py`.

**Checkpoint**: The page and the command return the same matched steps.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T009 Run the checks in `specs/026-deterministic-replay/quickstart.md` and confirm the existing suite stays green.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on T001. Blocks the stories.
- **User Story 1 (Phase 3)**: Depends on Phase 2.
- **User Story 2 (Phase 4)**: Depends on User Story 1, because the stop follows the matched prefix.
- **User Story 3 (Phase 5)**: Depends on User Story 2, because the page shows the stop sentence.
- **Polish (Phase 6)**: Depends on the stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Independently testable by replaying a finished workflow.
- **User Story 2 (P2)**: Independently testable once a completed prefix can be matched.
- **User Story 3 (P3)**: Independently testable once the report exists.

### Parallel Opportunities

- T003 and T007 touch different test files and can be written together.

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete User Story 1.
3. Stop and validate a repeated replay.

### Incremental Delivery

1. Match completed effects.
2. Stop at the first unfinished step.
3. Show the report on the task.

## Notes

- Do not write during replay.
- Do not rewrite the event replay.
- Commit only when the engineer asks.
