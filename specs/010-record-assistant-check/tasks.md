---
description: "Task list for Record One Check by the Assistant"
---

# Tasks: Record One Check by the Assistant

**Input**: Design documents from `/specs/010-record-assistant-check/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Included. Constitution Principle II requires a failing test before each behavior. The quickstart requires those tests to fail before the assistant check command exists.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested on its own.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Single project: `src/task_manager/`, `tests/` at the repository root

## Phase 1: Setup

**Purpose**: The one new table. `implementation_check` is not altered.

- [X] T001 Add `assistant_check` to `src/task_manager/storage/schema.sql` with `CREATE TABLE IF NOT EXISTS` only. `check_id` is the primary key and references `implementation_check(id)`. `assistant_name` is required and non-empty after trimming. No update or delete. Do not alter `implementation_check`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Every check can be read with an assistant name before any story command exists.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T002 [P] In `src/task_manager/storage/verification_store.py`, insert one `assistant_check` row for a new check id and extend `checks_for` with a left join. `assistant_name` is null when no row exists and the stored name when a row exists. Do not update or delete. Leave `passing_check` unchanged: it still uses the latest check by `checked_at`, then `id`, for each live criterion.
- [X] T003 [P] In `src/task_manager/storage/decision_store.py`, left-join `assistant_check` from `check_for_link`. In `src/task_manager/storage/task_store.py`, add `assistant_name` to the decision's check object. It is null when the engineer recorded the check or when the decision names no check.

**Checkpoint**: Engineer checks read back with `assistant_name` null. No assistant command exists yet.

---

## Phase 3: User Story 1 - Record one check of a carried-out change (Priority: P1) 🎯 MVP

**Goal**: The engineer submits one check the assistant already produced. The task shows the criterion wording, the evidence, Passed or Failed, the workspace assistant, and the time. The task stays In Progress.

**Independent Test**: On one In Progress task, record one ordinary change, then submit one Passed assistant check against one acceptance criterion. The check names the workspace assistant. The change stays Carried out, the criterion stays Unverified, and the task stays In Progress.

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T004 [P] [US1] Add failing unit tests in `tests/unit/test_assistant_check.py` for a Passed check and a Failed check that store the workspace assistant, the workspace engineer, and the workspace time; a client-supplied assistant name, engineer name, and time that are ignored; blank evidence `An account of the evidence is required.`; a bad result `Choose Passed or Failed.`; blank evidence winning over a bad result; Draft `The task must be In Progress.`; Ready `Start the task first.`; Completed `Reopen the task first.`; Cancelled `A cancelled task cannot be changed. Continued work is a new task.`; unknown task `Task not found.`; unknown change `Implementation change not found.`; a change on another task `The check must name a change on that task.`; no criterion `Choose an acceptance criterion.`; unknown criterion `Acceptance criterion not found.`; a criterion on another task `The check must name a criterion on that task.`; and an engineer check from `record_check` whose `assistant_name` is null. The task stays In Progress, the change stays Carried out, and the criterion stays Unverified. The command does not call a model and does not open a project file.
- [X] T005 [P] [US1] Add failing contract tests in `tests/contract/test_assistant_check_api.py` for `POST /api/tasks/{id}/assistant-checks` using the status codes and messages in `specs/010-record-assistant-check/contracts/http-api.md`. A missing `change_id` or a non-integer id is 400 `The request is missing a required field or has the wrong shape.` `POST /api/tasks/{id}/implementation-changes/{change_id}/checks` still stores no assistant name.

### Implementation for User Story 1

- [X] T006 [US1] Implement `record_assistant` in `src/task_manager/domain/verification.py`. Refuse in the order in `specs/010-record-assistant-check/data-model.md`. Then insert one `implementation_check` and one `assistant_check` in the same command. Copy the workspace assistant, the workspace engineer, and the workspace time. Trim the evidence. Store `passed` or `failed`. Do not change this path inside `record`.
- [X] T007 [US1] Add `record_assistant_check` to `src/task_manager/workspace.py`, `POST /api/tasks/{id}/assistant-checks` in `src/task_manager/web/api.py`, and the form and check line in `src/task_manager/web/pages.py` and `src/task_manager/web/templates/detail.html`, matching `specs/010-record-assistant-check/contracts/ui.md`. Ignore a client-supplied assistant name, engineer name, and time. The engineer check form stays on its current command.

**Checkpoint**: User Story 1 works. One request stores one check. An engineer check still names no assistant.

---

## Phase 4: User Story 2 - Let that check count, and stop the assistant there (Priority: P2)

**Goal**: A Failed assistant check keeps the existing completion sentence. A later Passed assistant check of that same pair lets the engineer complete the task. The assistant does not verify a criterion, record a decision, or complete the task.

**Independent Test**: On one In Progress task whose criterion is Verified and that has no subtasks, submit a Failed assistant check and try to complete the task. Then submit a later Passed assistant check of that same pair and have the engineer complete the task. The first attempt stays In Progress. The second becomes Completed.

### Tests for User Story 2 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T008 [US2] Add failing unit tests in `tests/unit/test_assistant_check.py` for a current Failed assistant check refusing completion with `Needs a passing check: Rename the export label.`; a later Passed assistant check of that same pair allowing completion when every other existing completion rule passes; the criterion staying Unverified until the engineer verifies it; the check adding no decision; and a decision the engineer records on that check showing the assistant name. A change Awaiting approval is refused with `The change must be carried out before it can be checked.` A change Not carried out is refused with `A change that was not carried out cannot be checked.`

### Implementation for User Story 2

- [X] T009 [US2] Do not add a completion sentence in `src/task_manager/domain/status.py`. Do not verify a criterion from `src/task_manager/domain/verification.py`. Do not insert a decision or a requirement run. The assistant check is an `implementation_check`, so the existing passing-check sentence already names the change.

**Checkpoint**: User Stories 1 and 2 both work. Recording the check does not complete the task.

---

## Phase 5: User Story 3 - Read the same check again (Priority: P3)

**Goal**: Opening the task shows the stored assistant check and does not store another one. A later check stays after the earlier one. A subtask check stays on the subtask.

**Independent Test**: Submit one assistant check, open the task, and replay that stored record. The second pass shows the same evidence, result, and assistant, and does not add a check.

### Tests for User Story 3 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T010 [P] [US3] Add failing unit tests in `tests/unit/test_assistant_check.py` for a later Passed check of the same change and criterion leaving the earlier Failed evidence unchanged, with Passed as the current result, and for an assistant check on a subtask that does not appear on the parent.
- [X] T011 [P] [US3] Extend `tests/integration/test_replay.py` so two fresh workspaces and the same script store one assistant check each. Opening each task does not add a check. The evidence, result, assistant, and order match. The script does not call a model and does not open a project file.

### Implementation for User Story 3

- [X] T012 [US3] Keep `checks_for` in `src/task_manager/storage/verification_store.py` read-only. Opening a task and replaying a stored check must not insert `implementation_check` or `assistant_check`.

**Checkpoint**: All three stories work. A stored check is not edited or removed.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: The manual quickstart.

- [X] T013 Run the manual checks in `specs/010-record-assistant-check/quickstart.md` against a fresh workspace.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on T001. Blocks every user story.
- **User Story 1 (Phase 3)**: Depends on Phase 2. No dependency on later stories.
- **User Story 2 (Phase 4)**: Depends on the assistant check from User Story 1. It does not add a new status rule.
- **User Story 3 (Phase 5)**: Depends on the stored check from User Story 1.
- **Polish (Phase 6)**: Depends on the stories being present.

### User Story Dependencies

- **User Story 1 (P1)**: Starts after T002 and T003. This is the MVP.
- **User Story 2 (P2)**: Starts after User Story 1 stores a check. T009 does not edit `status.py` when T008 passes.
- **User Story 3 (P3)**: Starts after User Story 1. T010 and T011 touch different test files and can run together.

### Within Each User Story

- Tests are written and fail before that story's implementation.
- The store read comes before the domain command.
- The domain command comes before the API and the page.
- A story is independently testable at its checkpoint.

### Parallel Opportunities

- T002 and T003 can run together after T001.
- T004 and T005 can run together.
- T010 and T011 can run together once User Story 1 is specified.

---

## Parallel Example: User Story 1

```bash
# Failing tests together, before implementation:
Task: "Unit tests in tests/unit/test_assistant_check.py"
Task: "Contract tests in tests/contract/test_assistant_check_api.py"

# After the domain command exists:
Task: "Workspace command in src/task_manager/workspace.py"
Task: "Task page form in src/task_manager/web/templates/detail.html"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3.
3. Stop and validate: one Passed assistant check, one engineer check with no assistant name, and an In Progress task.

### Incremental Delivery

1. Setup and foundation.
2. User Story 1: record one assistant check.
3. User Story 2: the existing completion hold counts that check.
4. User Story 3: replay and a later check.
5. Polish: the quickstart.

## Notes

- [P] tasks use different files and do not depend on an unfinished task.
- Do not commit unless the user asks.
- Do not rewrite specifications 001 through 009 or the constitution.
- The product stores the result the engineer submits. It does not call a model, open a file, or run a test.
