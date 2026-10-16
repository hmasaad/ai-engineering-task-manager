---
description: "Task list for Workflow Versioning and Migration"
---

# Tasks: Workflow Versioning and Migration

**Input**: Design documents from `/specs/025-workflow-versioning/`

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

**Purpose**: The version tables. No existing table is altered.

- [X] T001 Add `workflow_version`, `workflow_version_step`, and `workflow_migration` in `src/task_manager/storage/schema.sql` with `CREATE TABLE IF NOT EXISTS` only, as in `specs/025-workflow-versioning/data-model.md`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The current version can be read without writing, and advance uses it.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T002 Read and link versions in `src/task_manager/storage/workflow_store.py`. When a current version exists, `steps` returns that version. When steps exist and no version is stored, the steps are still returned and the version number is 1.

**Checkpoint**: Opening a workflow does not write a version row.

---

## Phase 3: User Story 1 - The running workflow keeps a version (Priority: P1) 🎯 MVP

**Goal**: The task shows version 1, and advance still runs that version.

**Independent Test**: Add two steps, advance once, and open the task again. The version is 1, the first step is Completed, and the second is Pending.

### Tests for User Story 1

- [X] T003 [P] [US1] Add the version checks in `tests/unit/test_workflow_versioning.py`. Confirm they fail before the behavior exists.

### Implementation for User Story 1

- [X] T004 [US1] Store version 1 when the first step is added in `src/task_manager/domain/workflow.py`. Report `version` from `payload`.

**Checkpoint**: The current version is visible and advance still performs one unfinished step.

---

## Phase 4: User Story 2 - Revise the remaining work (Priority: P2)

**Goal**: Revise creates one draft that keeps the steps that already ran.

**Independent Test**: Complete one step, revise, and add a replacement step. The draft has the completed step and the new step. The current version still has its pending step.

### Tests for User Story 2

- [X] T005 [P] [US2] Extend `tests/unit/test_workflow_versioning.py` for revise, a draft step, and the refusals in `specs/025-workflow-versioning/contracts/commands.md`.

### Implementation for User Story 2

- [X] T006 [US2] Add `revise` in `src/task_manager/domain/workflow.py` and `revise_workflow` in `src/task_manager/workspace.py`. Add the draft step through the existing add and remove commands.

**Checkpoint**: A refused revise leaves no draft.

---

## Phase 5: User Story 3 - Migrate onto the draft (Priority: P3)

**Goal**: A named migration makes the draft current and leaves the previous version superseded.

**Independent Test**: Migrate with `Replace the remaining step`. The next advance performs the new step once and does not perform the completed step or the superseded pending step.

### Tests for User Story 3

- [X] T007 [P] [US3] Extend `tests/unit/test_workflow_versioning.py` and add `tests/contract/test_workflow_versioning_api.py` for migration and the page.

### Implementation for User Story 3

- [X] T008 [US3] Add `migrate` in `src/task_manager/domain/workflow.py`. Expose it from `src/task_manager/web/api.py`, `src/task_manager/web/pages.py`, and `src/task_manager/web/templates/detail.html`.

**Checkpoint**: The superseded version and the reason remain after the task is opened again.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T009 Run the checks in `specs/025-workflow-versioning/quickstart.md` and confirm the existing suite stays green.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on T001. Blocks the stories.
- **User Story 1 (Phase 3)**: Depends on Phase 2.
- **User Story 2 (Phase 4)**: Depends on User Story 1, because the draft is the next version.
- **User Story 3 (Phase 5)**: Depends on User Story 2, because migration needs a draft.
- **Polish (Phase 6)**: Depends on the stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Independently testable by opening a workflow.
- **User Story 2 (P2)**: Independently testable once version 1 exists.
- **User Story 3 (P3)**: Independently testable once a draft exists.

### Parallel Opportunities

- T005 and the unit portion of T007 extend the same test file and stay sequential. The contract test file can be written beside the unit file.

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete User Story 1.
3. Stop and validate version 1.

### Incremental Delivery

1. Show version 1.
2. Revise into a draft.
3. Migrate with a reason.

## Notes

- Do not delete a superseded step.
- Do not rewrite the replay.
- Commit only when the engineer asks.
