---
description: "Task list for Workspace Boundaries and Capability-Based Permissions"
---

# Tasks: Workspace Boundaries and Capability-Based Permissions

**Input**: Design documents from `/specs/017-workspace-boundaries/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Included. `plan.md` and `quickstart.md` require these tests. The tests are the feature. Constitution Principle II requires them before any product change.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested on its own.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Single project: `src/task_manager/`, `tests/` at the repository root

## Phase 1: Setup

**Purpose**: No new storage. The workspace remains the file named at start.

- [X] T001 Leave `src/task_manager/storage/schema.sql` without a new table and without a new column. Do not add a capability table or a grant table.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: No new command and no permission screen. Existing commands stay the contract.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T002 [P] Leave `src/task_manager/web/api.py`, `src/task_manager/web/pages.py`, and `src/task_manager/web/templates/detail.html` without a new route and without a permission screen. The commands in `specs/017-workspace-boundaries/contracts/commands.md` stay the existing ones.

**Checkpoint**: Foundation ready. User stories add tests only, unless a test shows a boundary is already broken.

---

## Phase 3: User Story 1 - Keep one workspace separate, and keep it after a restart (Priority: P1) 🎯 MVP

**Goal**: Records written in one workspace file stay out of a second file. Closing and opening the same file shows the same task, status, and evidence.

**Independent Test**: Create a task, a status, and evidence in workspace A. Open workspace B and confirm it has none of those records. Create a different task in B and confirm A is unchanged. Close A and open it again. The original task, status, and evidence are still there.

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T003 [US1] Add tests in `tests/unit/test_workspace_boundary.py`. Open two `Workspace` values on two different files. In A, create a task, set a goal, add a criterion, mark it Ready, start it, verify the criterion with observation `The label text was read.`, and record a decision whose statement is `Keep the recorded label`. B lists no task and no requirement. A task created in B does not appear in A. Close A and open the same file again: the title, status `In Progress`, observation, and decision statement are unchanged. Open that file again with a different engineer name and confirm the stored observation and decision statement are not rewritten.

### Implementation for User Story 1

- [X] T004 [US1] If T003 fails, correct only the path handling in `src/task_manager/storage/connection.py` and `src/task_manager/workspace.py` so one `Workspace` reads and writes only the file it was given. Do not add a table. If T003 passes, leave both files unchanged.

**Checkpoint**: User Story 1 passes. Two workspace files stay separate, and a restart keeps the stored evidence.

---

## Phase 4: User Story 2 - Task records do not touch the repository (Priority: P2)

**Goal**: Creating and updating task records does not create, delete, or modify a project file and does not run a repository command.

**Independent Test**: In a repository that already has one commit and one changed file, record a task through to In Progress, verify a criterion, record an ordinary change that names no file, record a decision, and record a requirement. The repository files, the current commit, and the current branch are unchanged, and no repository command ran.

### Tests for User Story 2 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T005 [US2] Add tests to `tests/unit/test_workspace_boundary.py`. Use a temporary repository with one commit on branch `main` and a changed `label.txt`. Through `Workspace`, create a task, set its goal, add a criterion, mark it Ready, start it, verify the criterion, call `record_change` with a project name and no file, call `record_assistant_change` with no file, record a decision, and record a requirement. Opening the task again does not change the repository. Assert the file hashes, `HEAD`, and current branch are unchanged, and that no repository command ran. `list_requirements` on a second workspace file stays empty.

### Implementation for User Story 2

- [X] T006 [US2] If T005 fails, remove the project write or repository command from the task-record path that performed it. The allowed files are `src/task_manager/domain/capture.py`, `src/task_manager/domain/status.py`, `src/task_manager/domain/decisions.py`, `src/task_manager/domain/verification.py`, `src/task_manager/domain/requirement.py`, and `record` in `src/task_manager/domain/implementation.py`. Do not add a capability. If T005 passes, leave those files unchanged.

**Checkpoint**: User Stories 1 and 2 pass. Task records stay in the workspace file and leave the repository unchanged.

---

## Phase 5: User Story 3 - One capability authorizes one named target (Priority: P3)

**Goal**: Approving one waiting change does not carry out another. A file read does not write the file. The assistant cannot approve.

**Independent Test**: Approve a request to create branch `feature`. That approval checks out `feature` and does not commit a file. A separate waiting commit stays waiting until its own approval.

### Tests for User Story 3 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T007 [P] [US3] Add tests in `tests/unit/test_capability.py`. On one In Progress task in a repository with one commit and a changed `label.txt`, record a waiting branch `feature` and a waiting commit of `label.txt`. Approving only the branch checks out `feature`, adds no commit, and leaves the commit Awaiting approval. A file read of `label.txt` stores the text and leaves the file bytes unchanged. Assistant approval of the waiting commit returns `The assistant cannot approve a change.` and commits nothing. An ordinary request to create one new folder creates that folder and no other file.

### Implementation for User Story 3

- [X] T008 [US3] If T007 fails, correct `approve` in `src/task_manager/domain/implementation.py` so it carries out only the named change, and correct `read_file` in `src/task_manager/domain/file_read.py` so it does not write the file. Do not add a message or a permission screen. If T007 passes, leave both files unchanged.

**Checkpoint**: All three stories pass. One approval carries out one target.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Confirm the earlier commands still pass and this feature added no storage.

- [X] T009 Run `pytest` from the repository root and confirm `src/task_manager/storage/schema.sql` still has no table added by this feature. `tests/unit/test_commit_file.py` and `tests/unit/test_pull_request.py` stay green.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
- **Polish (Phase 6)**: Depends on User Stories 1, 2, and 3

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after User Story 1 - It adds cases to `tests/unit/test_workspace_boundary.py`
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Its tests are in a different file and do not depend on User Story 1 or 2

### Within Each User Story

- Tests MUST be written before any product change
- A product file changes only when its story test fails
- The story is complete when its test passes and no new command was added

### Parallel Opportunities

- T001 and T002 can run in parallel. They edit different files.
- T007 can run in parallel with T003. They edit different test files.
- T005 cannot run in parallel with T003. Both edit `tests/unit/test_workspace_boundary.py`.

---

## Parallel Example: User Story 3

```bash
# After T002, launch the two test files together:
Task: "Add workspace separation tests in tests/unit/test_workspace_boundary.py"
Task: "Add one-target capability tests in tests/unit/test_capability.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Add User Story 2 and User Story 3
6. Complete Phase 6: Polish

### Incremental Delivery

1. Complete Setup + Foundational → no new table and no new command
2. Add User Story 1 → two workspace files stay separate
3. Add User Story 2 → task records leave the repository unchanged
4. Add User Story 3 → one approval carries out one target
5. Polish confirms the existing suite stays green

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps the task to the user story it proves
- Each user story is independently testable
- Specifications 001 through 016 are not rewritten
- Do not add a sign-in step or a screen that grants capabilities in advance
