---
description: "Task list for Record Task Implementation"
---

# Tasks: Record Task Implementation

**Input**: Design documents from `/specs/002-record-implementation/`

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

**Purpose**: Add the stored tables this feature needs. The Python package, clock, and process shell already exist.

- [X] T001 Add `implementation_change` and `implementation_resolution` to `src/task_manager/storage/schema.sql` with `CREATE TABLE IF NOT EXISTS`, so an existing workspace file gains them when `src/task_manager/storage/connection.py` runs the script. `implementation_change` columns: `id` integer primary key assigned in insertion order; `task_id` required and references `task(id)`; `what_changed` required and non-empty after trimming; `class` required and exactly `ordinary` or `consequential`; `engineer_name` required and non-empty; `recorded_at` required. `implementation_resolution` columns: `change_id` primary key referencing `implementation_change(id)` so there is at most one row per change; `kind` exactly `approved` or `not_carried_out`; `evidence` non-empty and `reason` empty when `kind` is `approved`; `reason` non-empty and `evidence` empty when `kind` is `not_carried_out`; `engineer_name` required and non-empty; `resolved_at` required. Index `implementation_change(task_id)`. No update or delete statement for either table.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Read and insert the new rows without story rules. Every story lists changes through the existing task detail.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T002 Implement insert and read functions in `src/task_manager/storage/implementation_store.py` for `implementation_change` and `implementation_resolution`. Insert a change with `task_id`, trimmed `what_changed`, `class`, `engineer_name`, and `recorded_at`. Insert a resolution with `change_id`, `kind`, `evidence`, `reason`, `engineer_name`, and `resolved_at`. List a task's changes by `recorded_at` ascending, then `id` ascending. Return one change by id, and its resolution when present. Do not check task status. Do not add a function that updates or deletes either table.
- [X] T003 Add `implementation_changes` to the task detail returned by `task_detail` in `src/task_manager/storage/task_store.py`, using T002. Each item has `id`, `what_changed`, `class`, `outcome`, `engineer_name`, `recorded_at`, `approval`, and `not_carried_out`. Outcome is only this table: `ordinary` and no resolution is `Carried out`; `consequential` and no resolution is `Awaiting approval`; `consequential` and `kind = approved` is `Carried out`; `consequential` and `kind = not_carried_out` is `Not carried out`. `approval` is `{evidence, engineer_name, approved_at}` or null. `not_carried_out` is `{reason, engineer_name, declined_at}` or null. `approved_at` and `declined_at` are the stored `resolved_at`. An ordinary change has both objects null.

**Checkpoint**: Foundation ready — user story implementation can now begin

---

## Phase 3: User Story 1 - Attach what changed to an in-progress task (Priority: P1) 🎯 MVP

**Goal**: An engineer records what changed on an In Progress task. An ordinary change is Carried out. A consequential change is Awaiting approval. The task status does not change, and a later reader sees the change on that task only.

**Independent Test**: On one In Progress task, record one ordinary change. Open the task and confirm the description, the task, the engineer, and the time are visible, and the status is still In Progress.

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T004 [P] [US1] Add failing unit tests in `tests/unit/test_implementation.py` that call the domain record function and assert: a blank or whitespace `what_changed` is refused with `An account of what changed is required.` and writes no row; a missing or unknown `class` is refused with `Choose ordinary or consequential.` and writes no row; an `ordinary` change on an In Progress task is `Carried out`, stores `class` `ordinary`, copies the workspace engineer name `Ada` rather than a name from the caller, stores the scripted clock time, leaves status, criteria, decisions, and status history unchanged, and has no resolution row; a `consequential` change is `Awaiting approval` with no resolution row and does not change status; Draft is refused with `The task must be In Progress.`; Ready is refused with `Start the task first.`; Completed is refused with `Reopen the task first.`; Cancelled is refused with `A cancelled task cannot be changed. Continued work is a new task.`; two ordinary changes are listed oldest first by `recorded_at`, then `id`; a change recorded on one task is absent from another task's detail; an unknown task id is refused with `Task not found.`
- [X] T005 [P] [US1] Add failing contract tests in `tests/contract/test_implementation_api.py` for `POST /api/tasks/{id}/implementation-changes` and `GET /api/tasks/{id}` using the status codes and exact messages in `specs/002-record-implementation/contracts/http-api.md`. Assert the detail field `implementation_changes` and that a body field `engineer_name` is ignored. Assert a refused command returns `{"refused": true, "message": "..."}` and leaves the task status unchanged.

### Implementation for User Story 1

- [X] T006 [US1] Implement record in `src/task_manager/domain/implementation.py` so it satisfies `tests/unit/test_implementation.py`. Trim `what_changed` before the empty check. Accept `class` only as `ordinary` or `consequential`. Copy the engineer name from the workspace inside the command, never from the caller. Write the change through `src/task_manager/storage/implementation_store.py` and return the task detail. Do not approve, decline, complete, cancel, verify, or insert a decision.
- [X] T007 [US1] Add `record_change` to `src/task_manager/workspace.py` so it runs that domain function inside the existing transaction and clock.
- [X] T008 [US1] Add `POST /api/tasks/{id}/implementation-changes` to `src/task_manager/web/api.py` with body fields `what_changed` and `class`. Ignore extra fields, including `engineer_name`. Return the task detail or the refusal from `specs/002-record-implementation/contracts/http-api.md`.
- [X] T009 [US1] Show the change list and the record form on `src/task_manager/web/templates/detail.html`, and accept the form in `src/task_manager/web/pages.py` at `POST /tasks/{task_id}/implementation-changes`. Show the form only when the task is In Progress. The form asks for what changed and a choice of ordinary or consequential. A refusal redisplays the detail with the API message and the same stored task. A success redisplays the detail without changing the status.

**Checkpoint**: User Story 1 is functional on its own — record an ordinary or consequential change and read it back on that task

---

## Phase 4: User Story 2 - Approve a consequential change by name (Priority: P2)

**Goal**: A consequential change stays Awaiting approval until a separate command names it and records the evidence reviewed. Completing or cancelling the task is refused until then.

**Independent Test**: Record one consequential change, confirm it is Awaiting approval, then approve it with a non-empty account of the evidence reviewed and confirm it is Carried out, the task is still In Progress, and the approval names the evidence, the engineer, and the time.

### Tests for User Story 2 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T010 [P] [US2] Add failing unit tests in `tests/unit/test_implementation_approval.py` for approve and for the completion guard: blank evidence is refused with `An account of the evidence reviewed is required.` and writes no resolution; a successful approve on an In Progress task stores `kind` `approved`, evidence, workspace engineer `Ada`, and the clock time, sets outcome `Carried out`, and does not change task status, criteria, decisions, or history; approving an ordinary change is refused with `An ordinary change does not wait for approval.`; approving an already carried-out consequential change is refused with `The change is already carried out.` and the first approval is unchanged; saving the change without a later approve leaves it `Awaiting approval`; approve is refused with `The task must be In Progress.` when the task is not In Progress, even if a row was forced there; a change on another task is refused with `The approval must name a change on that task.`; an unknown change id is refused with `Implementation change not found.`; an unknown task id is refused with `Task not found.` Completion of an In Progress task whose criteria are all Verified, that has no unfinished subtask, and that has one Awaiting approval change stays In Progress, writes no status-change row, and is told `Awaiting approval: {what_changed}.` Cancellation with a reason does the same. Several waiting accounts are comma-separated, oldest first. When unverified criteria also block completion, the message keeps `Unverified criteria: ...` and also includes `Awaiting approval: ...`. When unfinished subtasks also block cancellation, the message keeps `Subtasks must be finished or cancelled first: ...` and also includes `Awaiting approval: ...`. A Carried out change does not add that sentence. After the waiting change is approved, completion succeeds when the feature 001 guards hold. With no waiting change, an unverified-criterion refusal stays the feature 001 message only.
- [X] T011 [P] [US2] Add failing contract tests in `tests/contract/test_implementation_approval_api.py` for `POST /api/tasks/{id}/implementation-changes/{change_id}/approve` and for `POST /api/tasks/{id}/transitions` actions `complete` and `cancel`, asserting the status codes and exact messages in `specs/002-record-implementation/contracts/http-api.md`, including `Awaiting approval: ` in the refusal and an unchanged feature 001 refusal when nothing is Awaiting approval.

### Implementation for User Story 2

- [X] T012 [US2] Implement approve in `src/task_manager/domain/implementation.py` so it satisfies the approve cases in `tests/unit/test_implementation_approval.py`. Insert one `approved` resolution through `src/task_manager/storage/implementation_store.py`. Refuse a second resolution. Do not change task status.
- [X] T013 [US2] Add `approve_change` to `src/task_manager/workspace.py` using the existing transaction and clock.
- [X] T014 [US2] Add `POST /api/tasks/{id}/implementation-changes/{change_id}/approve` to `src/task_manager/web/api.py` with body field `evidence`. Ignore a client engineer name.
- [X] T015 [US2] Add an approve form to `src/task_manager/web/templates/detail.html` and `POST /tasks/{task_id}/implementation-changes/{change_id}/approve` in `src/task_manager/web/pages.py`. Show it only for an Awaiting approval change on an In Progress task. Redisplay the detail with the refusal message or the updated change. Do not treat the record form as approval.
- [X] T016 [US2] Extend complete and cancel in `src/task_manager/domain/status.py` so an Awaiting approval change on that task refuses the command, leaves status In Progress, writes no status-change row, and names each waiting `what_changed` oldest first in `Awaiting approval: {accounts}.` Keep the existing unverified-criterion and unfinished-subtask sentences when those also apply. Do not let a Carried out change block either command. Do not list a subtask's waiting changes on the parent.

**Checkpoint**: User Stories 1 and 2 work — a consequential change can be approved, and it blocks completion and cancellation until then

---

## Phase 5: User Story 3 - Leave a consequential change uncarried (Priority: P3)

**Goal**: The engineer marks an Awaiting approval change not carried out, with a reason. It stays visible and cannot be approved. The task status does not change.

**Independent Test**: Record one consequential change, mark it not carried out with a reason, and confirm it remains visible, cannot be approved, and the task status is unchanged.

### Tests for User Story 3 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T017 [P] [US3] Add failing unit tests in `tests/unit/test_implementation_decline.py` for: a non-empty reason on an Awaiting approval change stores `kind` `not_carried_out`, the reason, workspace engineer `Ada`, and the clock time, outcome `Not carried out`, and does not change task status; a blank or whitespace reason is refused with `A reason is required.` and leaves the change Awaiting approval; a Carried out change, ordinary or consequential, is refused with `A carried-out change stays in the record.` and an existing approval is unchanged; marking an already Not carried out change again is refused with `It cannot be carried out.`; approving a Not carried out change is refused with `It cannot be carried out.`; a task that is not In Progress is refused with `The task must be In Progress.`; a change on another task is refused with `The change must be on that task.`; an unknown change id is refused with `Implementation change not found.`; after the only waiting change is marked not carried out, cancellation with a reason and no unfinished subtask succeeds, and completion succeeds when the feature 001 guards hold.
- [X] T018 [P] [US3] Add failing contract tests in `tests/contract/test_implementation_decline_api.py` for `POST /api/tasks/{id}/implementation-changes/{change_id}/not-carried-out` using the status codes and exact messages in `specs/002-record-implementation/contracts/http-api.md`. Assert the detail shows `not_carried_out.reason` and `declined_at`, and that a later approve is refused.

### Implementation for User Story 3

- [X] T019 [US3] Implement mark-not-carried-out in `src/task_manager/domain/implementation.py` so it satisfies `tests/unit/test_implementation_decline.py`. Insert one `not_carried_out` resolution. Refuse a second resolution. Do not change task status and do not delete the change.
- [X] T020 [US3] Add `mark_change_not_carried_out` to `src/task_manager/workspace.py` using the existing transaction and clock.
- [X] T021 [US3] Add `POST /api/tasks/{id}/implementation-changes/{change_id}/not-carried-out` to `src/task_manager/web/api.py` with body field `reason`. Ignore a client engineer name.
- [X] T022 [US3] Add the not-carried-out form to `src/task_manager/web/templates/detail.html` and `POST /tasks/{task_id}/implementation-changes/{change_id}/not-carried-out` in `src/task_manager/web/pages.py`. Show it only for an Awaiting approval change on an In Progress task. Show the reason on a Not carried out change. A Cancelled task shows its changes and offers none of the record, approve, or not-carried-out actions.

**Checkpoint**: All three stories work — waiting changes can be approved or left uncarried, and only a waiting change blocks completion and cancellation

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Replay and the quickstart

- [X] T023 Extend `tests/integration/test_replay.py` so the same script — record an ordinary change, record a consequential change, approve it, record another consequential change, and mark that one not carried out — run twice from an In Progress task with no implementation changes and the same `ScriptedClock`, produces the same outcomes and the same order
- [X] T024 Run the four manual scenarios in `specs/002-record-implementation/quickstart.md` against a fresh `workspace.db` and fix any mismatch in `src/task_manager/` before treating the feature as done

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **User Stories (Phase 3–5)**: Depend on Foundational
- **Polish (Phase 6)**: Depends on the user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Foundational. No dependency on other stories
- **User Story 2 (P2)**: Starts after User Story 1, because approve acts on a consequential change that story records, and the completion guard reads that outcome
- **User Story 3 (P3)**: Starts after User Story 2, because refusing to decline an already approved change needs approve. The not-carried-out rules are still tested on their own in `tests/unit/test_implementation_decline.py`

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Domain rules before the workspace method
- Workspace method before the HTTP route and the page
- Story checkpoint before the next story

### Parallel Opportunities

- T004 and T005 can run in parallel
- T010 and T011 can run in parallel
- T017 and T018 can run in parallel
- Story phases stay sequential because later stories extend `src/task_manager/domain/implementation.py`, `src/task_manager/web/api.py`, and `src/task_manager/web/templates/detail.html`
- T023 starts after those stories, because the replay script calls record, approve, and mark-not-carried-out

---

## Parallel Example: User Story 1

```bash
# Write the failing User Story 1 tests together:
Task: "T004 tests/unit/test_implementation.py"
Task: "T005 tests/contract/test_implementation_api.py"

# Then implement in order: T006 domain, T007 workspace, T008 API, T009 pages
```

## Parallel Example: User Story 2

```bash
Task: "T010 tests/unit/test_implementation_approval.py"
Task: "T011 tests/contract/test_implementation_approval_api.py"
```

## Parallel Example: User Story 3

```bash
Task: "T017 tests/unit/test_implementation_decline.py"
Task: "T018 tests/contract/test_implementation_decline_api.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Run `tests/unit/test_implementation.py` and `tests/contract/test_implementation_api.py`
5. Demo an ordinary change on an In Progress task before adding approval

### Incremental Delivery

1. Setup + Foundational → tables and the change list on the task detail
2. User Story 1 → record what changed (MVP)
3. User Story 2 → approve a consequential change, and block completion and cancellation while it waits
4. User Story 3 → mark a waiting change not carried out
5. Polish → replay test and quickstart scenarios

### Parallel Team Strategy

With multiple people:

1. Complete Setup and Foundational together
2. After that, one person owns User Story 1 through its checkpoint
3. The next stories follow in order because they share `src/task_manager/domain/implementation.py`, `src/task_manager/web/api.py`, and `src/task_manager/web/templates/detail.html`
4. Within a story, the failing tests can be written at the same time

---

## Notes

- [P] tasks = different files, no dependencies on incomplete work
- [US1]–[US3] map to the three stories in spec.md
- Verify each story's tests fail before implementing that story
- Do not infer the class from the wording of what changed
- Do not infer task completion from a recorded or approved change
- Commit after each task or logical group
- Stop at any checkpoint to validate that story alone
