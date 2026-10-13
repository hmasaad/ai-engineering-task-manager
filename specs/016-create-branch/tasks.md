---
description: "Task list for Create One Branch"
---

# Tasks: Create One Branch

**Input**: Design documents from `/specs/016-create-branch/`

**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Tests**: Included. `plan.md` requires unit tests and contract tests. Constitution Principle II requires a failing test before the behavior exists.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested on its own.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Single project: `src/task_manager/`, `tests/` at the repository root

## Phase 1: Setup

**Purpose**: The two new tables. Existing tables are not altered.

- [X] T001 Add `created_branch` and `created_branch_checkout` to `src/task_manager/storage/schema.sql` with `CREATE TABLE IF NOT EXISTS` only. `created_branch.change_id` is the primary key and references `implementation_change(id)`. `branch` is required and non-empty after trimming. `start_commit` is required and non-empty after trimming. `created_branch_checkout.change_id` is the primary key and references `created_branch(change_id)`. No update or delete.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: A change can be read with a branch before the checkout command exists.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T002 In `src/task_manager/storage/implementation_store.py`, insert one `created_branch` row and one `created_branch_checkout` row, and extend the change query with a left join. The payload key `created_branch` is null when no row exists. Otherwise it has `name`, `commit`, and `checked_out`. `checked_out` is false until a checkout row exists. Do not update or delete.

**Checkpoint**: A change with no branch reads `created_branch` as null. No branch command exists yet.

---

## Phase 3: User Story 1 - Create one branch after approval (Priority: P1) 🎯 MVP

**Goal**: On an In Progress task, the engineer names one new branch. The request waits. Approval creates that branch from the stored commit and checks it out. Opening the task again does not create another branch or check out again.

**Independent Test**: On one In Progress task, ask to create branch `feature` in an existing repository `billing`. Nothing is created and the task shows Awaiting approval. After the engineer approves, `feature` is the current branch, and a second opening does not create another branch or change the current branch.

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T003 [P] [US1] Add failing unit tests in `tests/unit/test_branch.py` for a waiting ordinary request that stores consequential, the workspace assistant, branch `feature`, and the starting commit, and that leaves the current branch unchanged; approval that checks out `feature` from that commit and leaves another branch in place; uncommitted work that stays uncommitted and adds no commit; opening the task after switching away that does not switch back; assistant approval `The assistant cannot approve a change.`; decline that creates nothing; a moved commit or a name that now exists `The branch no longer matches the commit this change was proposed against.` with the request staying Awaiting approval; a refusing checkout `The branch was refused.`; blank or illegal name `Name the branch this change creates.`; an existing branch `The branch already exists.`; a missing project `The project must already exist.`; a project that is not a repository `The project must already be a repository.`; a repository with no commit `The repository must already have a commit.`; and a stopped ordinary request that still waits. The task stays In Progress and the criterion stays Unverified. The command does not record a requirement run.
- [X] T004 [P] [US1] Add failing contract tests in `tests/contract/test_branch_api.py` for `POST /api/tasks/{id}/branches` and approval. A client-supplied assistant name is ignored. A blank branch is 400 `Name the branch this change creates.` A Draft task is 409 `The task must be In Progress.` before a blank project. `GET /api/requirements` stays empty.

### Implementation for User Story 1

- [X] T005 [US1] Implement `record` and `checkout_approved` in `src/task_manager/domain/branch.py`. Every request is stored as consequential and Awaiting approval. `stopped` is stored only when the request is ordinary and stopped. Approval runs `git switch -c` for that one branch, with no `--force`, no `--no-verify`, and no `git config`. A refusing command creates nothing and leaves the current branch in place. Opening the task does not call `checkout_approved`.
- [X] T006 [US1] Call `checkout_approved` from `approve` in `src/task_manager/domain/implementation.py` only when the change has a `created_branch` row and no checkout row. The assistant is refused before any checkout. Insert `created_branch_checkout` only after the checkout succeeds, in the same command as the approval.
- [X] T007 [US1] Add `record_branch` to `src/task_manager/workspace.py`, `POST /api/tasks/{id}/branches` in `src/task_manager/web/api.py`, `POST /tasks/{id}/branches` in `src/task_manager/web/pages.py`, and the form and branch line in `src/task_manager/web/templates/detail.html`. Ignore a client-supplied assistant name. Show `Branch {name} from {commit}` while the task is In Progress for the form.

**Checkpoint**: User Story 1 works. One request creates one branch after approval. A commit and a pull request keep their current commands.

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Keep the earlier repository commands unchanged.

- [X] T008 Confirm `src/task_manager/domain/commit_file.py` and `src/task_manager/domain/pull_request.py` are not given a branch-creation path, and that `tests/unit/test_commit_file.py` and `tests/unit/test_pull_request.py` still describe only their current rules.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS the user story
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion
- **Polish (Phase 4)**: Depends on User Story 1

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories

### Within User Story 1

- Tests MUST be written and FAIL before implementation
- The branch tables and the change payload come before `record`
- `record` and `checkout_approved` come before the approval hook and the page
- The story is complete before polish

### Parallel Opportunities

- T003 and T004 can run in parallel after T002. They edit different test files.
- T006 and T007 both depend on T005. They edit different files and can run in parallel with each other.

---

## Parallel Example: User Story 1

```bash
# Launch both test files together, after T002:
Task: "Add failing unit tests in tests/unit/test_branch.py"
Task: "Add failing contract tests in tests/contract/test_branch_api.py"

# After T005, launch the approval hook and the page together:
Task: "Call checkout_approved from approve in src/task_manager/domain/implementation.py"
Task: "Add record_branch, the HTTP command, and the task-page form"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Complete Phase 4: Polish

### Incremental Delivery

1. Complete Setup + Foundational → a change can carry a branch record
2. Add User Story 1 → Test independently → one approved branch is checked out
3. Polish confirms a commit and a pull request are unchanged

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps the task to User Story 1
- User Story 1 is independently completable and testable
- Verify tests fail before implementing
- Specifications 001 through 015 are not rewritten
