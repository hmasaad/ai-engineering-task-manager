---
description: "Task list for Verify a Recorded Change"
---

# Tasks: Verify a Recorded Change

**Input**: Design documents from `/specs/003-verify-implementation/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Included. Constitution Principle II and plan.md require a failing test for each behavior before that behavior is implemented. A passing test that does not map to a spec scenario does not count.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested on its own.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/task_manager/`, `tests/` at repository root
- Paths follow plan.md: `src/task_manager/domain/`, `src/task_manager/storage/`, `src/task_manager/web/`
- Tests use the existing `workspace` and `client` fixtures in `tests/conftest.py`. The workspace engineer is `Ada`. The scripted clock supplies timestamps.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add the stored table this feature needs. The Python package, clock, and process shell already exist.

- [X] T001 Add `implementation_check` to `src/task_manager/storage/schema.sql` with `CREATE TABLE IF NOT EXISTS`, so an existing workspace file gains it when `src/task_manager/storage/connection.py` runs the script. Columns: `id` integer primary key assigned in insertion order; `change_id` required and references `implementation_change(id)`; `criterion_id` required at insert and not a foreign key; `criterion_text` required and non-empty; `evidence` required and non-empty after trimming; `result` required and exactly `passed` or `failed`; `engineer_name` required and non-empty; `checked_at` required. Index `implementation_check(change_id)`. No update or delete statement for this table.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Insert and list checks without story rules. Every story reads checks through the existing task detail.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T002 Implement insert and read functions in `src/task_manager/storage/verification_store.py` for `implementation_check`. Insert a check with `change_id`, `criterion_id`, `criterion_text`, trimmed `evidence`, `result` of `passed` or `failed`, `engineer_name`, and `checked_at`. List a change's checks by `checked_at` ascending, then `id` ascending. Do not check task status, change outcome, or whether the criterion still exists. Do not add a function that updates or deletes the table.
- [X] T003 Add `checks` to each item in `implementation_changes` on the task detail returned by `task_detail` in `src/task_manager/storage/task_store.py`, using T002. Each check has `id`, `criterion_id`, `criterion_text`, `evidence`, `result`, `engineer_name`, and `checked_at`. Map stored `passed` to `Passed` and stored `failed` to `Failed`. Leave feature 001 and feature 002 fields unchanged. Do not add `passing_check` in this task.

**Checkpoint**: Foundation ready — user story implementation can now begin

---

## Phase 3: User Story 1 - Check a carried-out change against a criterion (Priority: P1) 🎯 MVP

**Goal**: An engineer records a check of one carried-out change against one acceptance criterion of the same In Progress task. The check stores the criterion wording, the evidence, Passed or Failed, the engineer, and the time. The task status, the change outcome, and the criterion's Verified state do not change.

**Independent Test**: On one In Progress task, record one ordinary change, then record a passing check of that change against one acceptance criterion, and read the check back on the task. The task status and the change outcome stay as they were.

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T004 [P] [US1] Add failing unit tests in `tests/unit/test_verification.py` that call the domain record-check function and assert: blank or whitespace evidence is refused with `An account of the evidence is required.` and writes no row; a missing result, or a result other than `Passed` or `Failed`, is refused with `Choose Passed or Failed.` and writes no row; a missing criterion id is refused with `Choose an acceptance criterion.` and writes no row; when evidence is blank and the result is also invalid, the refusal is `An account of the evidence is required.`; a `Passed` check of a carried-out ordinary change on an In Progress task stores `result` `passed`, copies `criterion_text` from the criterion at that moment, copies the workspace engineer name `Ada` rather than a name from the caller, stores the scripted clock time, leaves task status, change outcome, criterion Verified state, decisions, and status history unchanged; a `Failed` check stores `result` `failed` and leaves the change `Carried out` and the task `In Progress`; Draft is refused with `The task must be In Progress.`; Ready is refused with `Start the task first.`; Completed is refused with `Reopen the task first.`; Cancelled is refused with `A cancelled task cannot be changed. Continued work is a new task.`; a wrong status is refused before a blank body is considered; an Awaiting approval change is refused with `The change must be carried out before it can be checked.`; a Not carried out change is refused with `A change that was not carried out cannot be checked.`; a carried-out consequential change can be checked the same way as an ordinary one; a change on another task is refused with `The check must name a change on that task.`; a criterion on another task is refused with `The check must name a criterion on that task.`; an unknown task id is refused with `Task not found.`; an unknown change id is refused with `Implementation change not found.`; an unknown criterion id is refused with `Acceptance criterion not found.`
- [X] T005 [P] [US1] Add failing contract tests in `tests/contract/test_verification_api.py` for `POST /api/tasks/{id}/implementation-changes/{change_id}/checks` and `GET /api/tasks/{id}` using the status codes and exact messages in `specs/003-verify-implementation/contracts/http-api.md`. Assert the change's `checks` array and that a body field `engineer_name` is ignored. Assert a refused command returns `{"refused": true, "message": "..."}` and leaves the task status and the change outcome unchanged.

### Implementation for User Story 1

- [X] T006 [US1] Implement record-check in `src/task_manager/domain/verification.py` so it satisfies `tests/unit/test_verification.py`. Consider task status before the change, the criterion, the evidence, and the result. Accept `result` only as `Passed` or `Failed`, and store `passed` or `failed`. Copy `criterion_text` from the live criterion inside the command. Copy the engineer name from the workspace inside the command, never from the caller. Write the check through `src/task_manager/storage/verification_store.py` and return the task detail. Do not verify or unverify a criterion, approve a change, complete, cancel, or insert a decision.
- [X] T007 [US1] Add `record_check` to `src/task_manager/workspace.py` so it runs that domain function inside the existing transaction and clock.
- [X] T008 [US1] Add `POST /api/tasks/{id}/implementation-changes/{change_id}/checks` to `src/task_manager/web/api.py` with body fields `criterion_id`, `evidence`, and `result`. Ignore extra fields, including `engineer_name`. Return the task detail or the refusal from `specs/003-verify-implementation/contracts/http-api.md`.
- [X] T009 [US1] Show each change's checks and the record-check form on `src/task_manager/web/templates/detail.html`, and accept the form in `src/task_manager/web/pages.py` at `POST /tasks/{task_id}/implementation-changes/{change_id}/checks`. Show the form only when that change is Carried out and the task is In Progress. The form asks for a criterion from this task, the evidence, and a choice of Passed or Failed. A refusal redisplays the detail with the API message and the same stored task. A success redisplays the detail without changing the status or the change outcome. A Cancelled task shows its checks and does not offer the form.

**Checkpoint**: User Story 1 is functional on its own — record a Passed or Failed check and read it back on that change

---

## Phase 4: User Story 2 - Finish the task only when each carried-out change has passed (Priority: P2)

**Goal**: Completing a task is refused while any carried-out change on that task lacks a passing check. The refusal names each such change. Cancellation is not refused for that reason.

**Independent Test**: On one In Progress task whose acceptance criteria are already Verified and that has no subtasks, record one ordinary change and attempt to complete the task before any check. Then record a passing check and complete the task.

### Tests for User Story 2 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T010 [P] [US2] Add failing unit tests in `tests/unit/test_verification_completion.py` for the completion guard on one check: an In Progress task whose criteria are all Verified, that has no unfinished subtask, and that has one carried-out change with no check stays In Progress, writes no status-change row, and is told `Needs a passing check: {what_changed}.`; the same task with that change's only check `Failed` does the same; the same task with that change's only check `Passed` becomes Completed; a Not carried out change does not add that sentence, and completion succeeds when the feature 001 guards hold; a task with no implementation changes still completes under the feature 001 guards; an Awaiting approval change is still told only with `Awaiting approval: {what_changed}.` and is not also listed under `Needs a passing check:`; when both an Awaiting approval change and a carried-out change with no check exist, the message includes both sentences; several carried-out changes that lack a passing check are comma-separated, oldest first, and a change that has a passing check is omitted; when unverified criteria also block completion, the message keeps `Unverified criteria: ...` and also includes `Needs a passing check: ...`; when unfinished subtasks also block, the message keeps `Unfinished subtasks: ...`; sentence order is unverified criteria, unfinished subtasks, awaiting approval, then needs a passing check; cancellation with a reason and no unfinished subtask succeeds while a carried-out change has no check, and the cancel message does not contain `Needs a passing check:`; a subtask's missing check is not named on the parent. With no carried-out change lacking a passing check, an unverified-criterion refusal stays the earlier message only.
- [X] T011 [P] [US2] Add failing contract tests in `tests/contract/test_verification_completion_api.py` for `POST /api/tasks/{id}/transitions` action `complete`, asserting the status codes and exact messages in `specs/003-verify-implementation/contracts/http-api.md`, including `Needs a passing check: ` in the refusal, `passing_check` false before a passing check and true after the only check is `Passed`, and an unchanged cancel refusal that does not contain `Needs a passing check:`.

### Implementation for User Story 2

- [X] T012 [US2] Implement the single-check passing rule in `src/task_manager/domain/verification.py`. A carried-out change lacks a passing check when it has no check, or when its only check against a criterion that still exists on the task is `Failed`. One `Passed` check against a criterion that still exists means it has a passing check. Awaiting approval and Not carried out changes do not lack a passing check for this rule. Return the lacking changes' `what_changed` values oldest by `recorded_at`, then `id`.
- [X] T013 [US2] Add derived `passing_check` to each implementation change in `task_detail` in `src/task_manager/storage/task_store.py`, using the rule from T012. `passing_check` is not a column. It is true only for a Carried out change whose single existing check against a live criterion is `Passed`.
- [X] T014 [US2] Extend complete in `src/task_manager/domain/status.py` so a carried-out change on that task that lacks a passing check refuses completion, leaves status In Progress, writes no status-change row, and names each such `what_changed` oldest first in `Needs a passing check: {accounts}.` Keep the existing unverified-criterion, unfinished-subtask, and awaiting-approval sentences in that order when those also apply. Do not add this sentence to cancel. Do not list a subtask's changes on the parent. Do not list an Awaiting approval change in the needs-a-passing-check sentence.

**Checkpoint**: User Stories 1 and 2 work — one passing check lets the task be completed, and a missing or failed check does not

---

## Phase 5: User Story 3 - Record a later check without erasing the earlier one (Priority: P3)

**Goal**: A later check of the same change stays beside the earlier one. The current result of a change and a criterion is the latest check of that pair. The change has a passing check only when every criterion it has been checked against that still exists has a current result of Passed.

**Independent Test**: On one carried-out change, record a Failed check against one criterion, then a Passed check against the same criterion, and confirm both appear in that order with Passed as the current result.

### Tests for User Story 3 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T015 [P] [US3] Add failing unit tests in `tests/unit/test_verification_history.py` for: a later `Passed` check of a pair whose earlier check is `Failed` leaves the earlier evidence, result, engineer, and time unchanged, lists the checks oldest first, and makes that pair's current result `Passed`; a later `Failed` check of a pair whose current result is `Passed` makes the current result `Failed`, and completion of a task that otherwise may be completed stays In Progress with `Needs a passing check: {what_changed}.`; a `Passed` check against one criterion and a current `Failed` check against another criterion on the same change makes `passing_check` false and completion stays In Progress; a current `Passed` result for every checked live criterion makes `passing_check` true and completion succeeds when the earlier guards hold; editing the live criterion text does not rewrite `criterion_text` on an existing check; removing a criterion does not delete its checks, those checks stay readable with the stored wording, and they no longer count toward `passing_check`; there is no domain function that updates or deletes a check, and a second record inserts a new row.
- [X] T016 [P] [US3] Add failing contract tests in `tests/contract/test_verification_history_api.py` for two `POST /api/tasks/{id}/implementation-changes/{change_id}/checks` calls on one change. Assert `GET /api/tasks/{id}` returns both checks in order, the first check's `evidence` and `result` unchanged, and `passing_check` false when one live criterion's latest result is `Failed` and true when every checked live criterion's latest result is `Passed`. Assert no request can edit or delete a stored check.

### Implementation for User Story 3

- [X] T017 [US3] Extend the passing-check rule in `src/task_manager/domain/verification.py` and the `passing_check` value in `src/task_manager/storage/task_store.py` so they satisfy `tests/unit/test_verification_history.py`. The current result of one change and one criterion is the latest check of that pair by `checked_at`, then `id`. A change has a passing check only when at least one check names a criterion that still exists on that task and every such criterion's current result is `Passed`. A current `Failed` on any of those criteria means `passing_check` is false. Checks whose `criterion_id` no longer matches a criterion on the task stay in `checks` and are excluded from the test. Do not rewrite `criterion_text` when the live criterion text changes.
- [X] T018 [US3] Keep `src/task_manager/storage/verification_store.py` insert-only. `record_check` in `src/task_manager/domain/verification.py` must insert a new `implementation_check` row for a later check and must not update or delete an earlier row.

**Checkpoint**: All three stories work — later checks stay in the record, and completion waits until every checked criterion is currently Passed

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Replay and the quickstart

- [X] T019 Extend `tests/integration/test_replay.py` so the same script — record an ordinary change, record a `Failed` check against one criterion, record a `Passed` check of that same pair, and record a `Passed` check of a second criterion — run twice from an In Progress task with that change and no checks and the same `ScriptedClock`, produces the same results and the same order
- [X] T020 Run the three manual scenarios in `specs/003-verify-implementation/quickstart.md` against a fresh `workspace.db` and fix any mismatch in `src/task_manager/` before treating the feature as done

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **User Stories (Phase 3–5)**: Depend on Foundational
- **Polish (Phase 6)**: Depends on the user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Foundational. No dependency on other stories
- **User Story 2 (P2)**: Starts after User Story 1, because the completion guard reads a check that story records
- **User Story 3 (P3)**: Starts after User Story 2, because a later check changes the passing-check result that story uses for completion. The history rules are still tested on their own in `tests/unit/test_verification_history.py`

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Domain rules before the workspace method
- Workspace method before the HTTP route and the page
- Story checkpoint before the next story

### Parallel Opportunities

- T004 and T005 can run in parallel
- T010 and T011 can run in parallel
- T015 and T016 can run in parallel
- Story phases stay sequential because later stories extend `src/task_manager/domain/verification.py`, `src/task_manager/storage/task_store.py`, `src/task_manager/web/api.py`, and `src/task_manager/web/templates/detail.html`
- T019 starts after those stories, because the replay script calls record-check more than once

---

## Parallel Example: User Story 1

```bash
# Write the failing User Story 1 tests together:
Task: "T004 tests/unit/test_verification.py"
Task: "T005 tests/contract/test_verification_api.py"

# Then implement in order: T006 domain, T007 workspace, T008 API, T009 pages
```

## Parallel Example: User Story 2

```bash
Task: "T010 tests/unit/test_verification_completion.py"
Task: "T011 tests/contract/test_verification_completion_api.py"
```

## Parallel Example: User Story 3

```bash
Task: "T015 tests/unit/test_verification_history.py"
Task: "T016 tests/contract/test_verification_history_api.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Run `tests/unit/test_verification.py` and `tests/contract/test_verification_api.py`
5. Demo a Passed check on a carried-out change before gating completion

### Incremental Delivery

1. Setup + Foundational → table and the check list on the task detail
2. User Story 1 → record a check (MVP)
3. User Story 2 → refuse completion until that check passed, and still allow cancellation
4. User Story 3 → keep later checks, and require every checked criterion to be currently Passed
5. Polish → replay test and quickstart scenarios

### Parallel Team Strategy

With multiple people:

1. Complete Setup and Foundational together
2. After that, one person owns User Story 1 through its checkpoint
3. The next stories follow in order because they share `src/task_manager/domain/verification.py`, `src/task_manager/storage/task_store.py`, and the task detail
4. Within a story, the failing tests can be written at the same time

---

## Notes

- [P] tasks = different files, no dependencies on incomplete work
- [US1]–[US3] map to the three stories in spec.md
- Verify each story's tests fail before implementing that story
- Do not infer Passed or Failed from the wording of the evidence
- Do not mark a criterion Verified because a check was recorded
- Do not refuse cancellation because a carried-out change lacks a passing check
- Commit after each task or logical group
- Stop at any checkpoint to validate that story alone
