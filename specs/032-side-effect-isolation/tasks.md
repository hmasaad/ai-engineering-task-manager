---
description: "Task list for Deterministic Replay and Side-Effect Isolation"
---

# Tasks: Deterministic Replay and Side-Effect Isolation

**Input**: Design documents from `/specs/032-side-effect-isolation/`

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

**Purpose**: The seal table. No existing table is altered.

- [X] T001 Add `workflow_isolated_effect` in `src/task_manager/storage/schema.sql` with `CREATE TABLE IF NOT EXISTS` only, as in `specs/032-side-effect-isolation/data-model.md`. `step_id` is unique. `effect` is trimmed and not empty.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: One seal can be stored and read for a completed step.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T002 Read and insert sealed effects in `src/task_manager/storage/workflow_store.py`. A second insert for the same step does not add a row.

**Checkpoint**: A seal can be stored beside its step.

---

## Phase 3: User Story 1 - A completed step seals its effect (Priority: P1) 🎯 MVP

**Goal**: Completing a step seals its path in the same result.

**Independent Test**: A successful read has one seal. A missing file has none.

### Tests for User Story 1

- [X] T003 [P] [US1] Add the seal checks in `tests/unit/test_side_effect_isolation.py`. Confirm they fail before the behavior exists.

### Implementation for User Story 1

- [X] T004 [US1] Seal the effect inside the completion result in `src/task_manager/domain/workflow.py`. A failed step and a waiting step seal nothing.

**Checkpoint**: A rolled-back completion leaves no seal.

---

## Phase 4: User Story 2 - Replay uses the seal and leaves the project alone (Priority: P2)

**Goal**: Replay matches the seals after the project file is gone.

**Independent Test**: Remove `note.txt` after the read completes. Replay still names it, and the file stays gone.

### Tests for User Story 2

- [X] T005 [P] [US2] Extend `tests/unit/test_side_effect_isolation.py` for a removed file, a removed folder, a repeated replay, and the clock.

### Implementation for User Story 2

- [X] T006 [US2] Add `replay_isolated` in `src/task_manager/domain/workflow.py`. Use the sentences in `specs/032-side-effect-isolation/contracts/commands.md`. Do not open the project.

**Checkpoint**: A second replay returns the same report.

---

## Phase 5: User Story 3 - The task shows the sealed replay (Priority: P3)

**Goal**: The page shows the sealed effects and Replay isolated effects.

**Independent Test**: The page shows the sealed file, and the button does not read it again.

### Tests for User Story 3

- [X] T007 [P] [US3] Add `tests/contract/test_side_effect_isolation_api.py` for the page and `POST /api/tasks/{id}/workflow/replay-isolated`.

### Implementation for User Story 3

- [X] T008 [US3] Show the sealed replay in `src/task_manager/web/templates/detail.html` and accept the command in `src/task_manager/web/api.py`, `src/task_manager/web/pages.py`, and `src/task_manager/workspace.py`.

**Checkpoint**: The page and the command agree on the sealed effect.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T009 Run the checks in `specs/032-side-effect-isolation/quickstart.md` and confirm the existing suite stays green.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on T001. Blocks the stories.
- **User Story 1 (Phase 3)**: Depends on Phase 2.
- **User Story 2 (Phase 4)**: Depends on User Story 1, because replay reads the seals.
- **User Story 3 (Phase 5)**: Depends on User Story 2, because the page shows the replay.
- **Polish (Phase 6)**: Depends on the stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Independently testable by completing one read.
- **User Story 2 (P2)**: Independently testable once a seal exists.
- **User Story 3 (P3)**: Independently testable once the report is on the task.

### Parallel Opportunities

- T005 and T007 touch different test files and can be written together.

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete User Story 1.
3. Stop and validate one seal per completion.

### Incremental Delivery

1. Seal the effect with the completion.
2. Replay from the seal after the project file is gone.
3. Show the replay on the task.

## Notes

- Do not open the project during replay.
- Do not replace the existing execution replay.
- Commit only when the engineer asks.
