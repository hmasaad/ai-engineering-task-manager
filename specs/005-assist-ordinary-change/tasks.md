---
description: "Task list for Assist an Ordinary Change"
---

# Tasks: Assist an Ordinary Change

**Input**: Design documents from `/specs/005-assist-ordinary-change/`

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
- Tests use the existing `workspace` and `client` fixtures in `tests/conftest.py`. The workspace engineer is `Ada`. The scripted clock supplies timestamps. The configured assistant name defaults to `Assistant` unless a test sets `Guide`.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add the stored tables this feature needs. The Python package, clock, and process shell already exist.

- [X] T001 Add `workspace_assistant` and `assistant_change` to `src/task_manager/storage/schema.sql` with `CREATE TABLE IF NOT EXISTS`, so an existing workspace file gains them when `src/task_manager/storage/connection.py` runs the script. `workspace_assistant` has `id` required and always 1, and `assistant_name` required and non-empty after trimming. `assistant_change` has `change_id` required, the primary key, unique, and references `implementation_change(id)`; `project` required and non-empty after trimming; `assistant_name` required and non-empty after trimming; `stopped` required and exactly `0` or `1`. At most one row per change. No update or delete statement for `assistant_change`. Do not add a column to `implementation_change`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Save the assistant name and attach an assistant row to a change. Every story reads changes through the existing task detail.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T002 Save the configured assistant name in `src/task_manager/storage/connection.py`. On open, ensure `workspace_assistant` row `id` 1 exists. Default `assistant_name` is `Assistant` when the caller does not set one. The name is non-empty after trimming. Do not take the name from a change request. Changing it later must not rewrite `assistant_change` rows.
- [X] T003 Implement insert and read functions in `src/task_manager/storage/implementation_store.py` for `assistant_change`. Insert one row with `change_id`, trimmed `project`, `assistant_name`, and `stopped` of `0` or `1`. Read that row for one change id, or report that no row exists. Do not check task status or class. Do not add a function that updates or deletes `assistant_change` or `implementation_change`.
- [X] T004 Add `project`, `assistant_name`, `recorded_by`, and `stopped` to each change returned by `change_payload` in `src/task_manager/storage/implementation_store.py`, using T003. When no `assistant_change` row exists, `project` is null, `assistant_name` is null, `recorded_by` is `engineer`, and `stopped` is false. When a row exists, `recorded_by` is `assistant`, `project` and `assistant_name` come from that row, and `stopped` is true only when the stored `stopped` value is `1`. Keep `engineer_name` as the workspace engineer. Leave feature 002, feature 003, and feature 004 fields unchanged.

**Checkpoint**: Foundation ready — user story implementation can now begin

---

## Phase 3: User Story 1 - Carry out one ordinary change (Priority: P1) 🎯 MVP

**Goal**: An engineer asks the assistant to carry out one ordinary change for an In Progress task in a named project. The task shows the account, the project, the assistant, and Carried out. The task stays In Progress.

**Independent Test**: On one In Progress task, ask the assistant to carry out one ordinary change in a named project, then read the task. The change is Carried out, names the assistant and the project, and the task stays In Progress.

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T005 [P] [US1] Add failing unit tests in `tests/unit/test_assistant_change.py` that call the domain function for an ordinary assistant change and assert: a blank or whitespace project is refused with `Name the project this change is for.` and writes no change row and no `assistant_change` row; a blank or whitespace account is refused with `An account of what changed is required.` and writes nothing; when the project and the account are both blank, the refusal is `Name the project this change is for.`; a missing class, or a class other than `ordinary` or `consequential`, is refused with `Choose ordinary or consequential.` and writes nothing; an ordinary change on an In Progress task stores `class` `ordinary`, outcome Carried out, `project` `billing`, `assistant_name` `Guide` rather than a name from the caller, `recorded_by` `assistant`, `stopped` false, `engineer_name` `Ada`, and the scripted clock time; task status, criterion Verified state, checks, decisions, and status history stay unchanged; the command does not create a directory or file for `billing`; Draft is refused with `The task must be In Progress.`; Ready is refused with `Start the task first.`; Completed is refused with `Reopen the task first.`; Cancelled is refused with `A cancelled task cannot be changed. Continued work is a new task.`; a wrong status is refused before a blank project is considered; an unknown task id is refused with `Task not found.`
- [X] T006 [P] [US1] Add failing contract tests in `tests/contract/test_assistant_change_api.py` for `POST /api/tasks/{id}/assistant-changes` and `GET /api/tasks/{id}` using the status codes and exact messages in `specs/005-assist-ordinary-change/contracts/http-api.md`. Assert the new change is last in `implementation_changes`, `recorded_by` is `assistant`, and body fields `assistant_name` and `engineer_name` are ignored. Assert a refused command returns `{"refused": true, "message": "..."}` and leaves the task status unchanged. Assert a wrong-shaped body is 400 with `The request is missing a required field or has the wrong shape.`

### Implementation for User Story 1

- [X] T007 [US1] Implement the ordinary assistant-change command in `src/task_manager/domain/implementation.py` so it satisfies `tests/unit/test_assistant_change.py`. Consider the task, then the status, then the project, then the account, then the class. For `ordinary` with no stop, insert an `implementation_change` of class `ordinary` and an `assistant_change` row with `stopped` `0` through `src/task_manager/storage/implementation_store.py`. Copy `assistant_name` from `workspace_assistant`, never from the caller. Keep `implementation_change.engineer_name` as the workspace engineer. Return the task detail. Do not store a consequential request or a stop in this task. Do not open or write the named project. Do not verify a criterion, record a check, record a decision, or change task status. Leave `record` unchanged.
- [X] T008 [US1] Add `record_assistant_change` to `src/task_manager/workspace.py` so it runs that domain function inside the existing transaction and clock. Add an `assistant_name` argument to `Workspace`, default `Assistant`, and pass it through T002.
- [X] T009 [US1] Add `POST /api/tasks/{id}/assistant-changes` to `src/task_manager/web/api.py` with body fields `project`, `class`, and `what_changed`. Ignore extra fields, including `assistant_name` and `engineer_name`. Return the task detail or the refusal from `specs/005-assist-ordinary-change/contracts/http-api.md`.
- [X] T010 [US1] Show `project` and `assistant_name` on an assistant change, and add the assistant-change form, on `src/task_manager/web/templates/detail.html`. Accept the form in `src/task_manager/web/pages.py` at `POST /tasks/{task_id}/assistant-changes`. Show the form only when the task is In Progress. The form asks for a project, a class, and an account of what changed. A refusal redisplays the detail with the API message and the same stored task. A success redisplays the detail without changing the status. A Cancelled task shows stored assistant fields and does not offer the form.
- [X] T011 [US1] Add `--assistant` to `src/task_manager/__main__.py`, default `Assistant`, and pass that name into `Workspace`. Do not let the flag rewrite assistant names already stored on changes.

**Checkpoint**: User Story 1 is functional on its own — record one ordinary assistant change and read the project, the assistant, and Carried out on that task

---

## Phase 4: User Story 2 - Stop a consequential change for approval (Priority: P2)

**Goal**: A consequential request is not carried out. The task shows Awaiting approval. An ordinary request that the assistant stops is stored the same way. The engineer approves or declines later. The assistant cannot approve or decline.

**Independent Test**: On one In Progress task, ask the assistant for a consequential change in a named project. The change shows Awaiting approval, and the task stays In Progress until the engineer approves or declines.

### Tests for User Story 2 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T012 [P] [US2] Add failing unit tests in `tests/unit/test_assistant_approval.py` for: a consequential request stores `class` `consequential`, outcome Awaiting approval, `stopped` false, `recorded_by` `assistant`, and does not create a file for the named project; an ordinary request with the stop set stores `class` `consequential`, `stopped` true, and outcome Awaiting approval; an approve call whose actor is `assistant` is refused with `The assistant cannot approve a change.` and writes no resolution; a decline call whose actor is `assistant` is refused with `The assistant cannot decline a change.` and leaves the change Awaiting approval; the engineer can approve that waiting change with non-empty evidence, the approval `engineer_name` is `Ada`, and the outcome becomes Carried out; the engineer can mark a waiting assistant change not carried out with a reason, and a later approve is refused with the existing feature 002 message.
- [X] T013 [P] [US2] Add failing contract tests in `tests/contract/test_assistant_approval_api.py` for `POST /api/tasks/{id}/assistant-changes` with `class` `consequential` and with `class` `ordinary` plus `stopped` true, and for approve and decline with `actor` `assistant`. Assert the status codes and exact messages in `specs/005-assist-ordinary-change/contracts/http-api.md`. Assert a successful engineer approval names `Ada` in `approval.engineer_name`.

### Implementation for User Story 2

- [X] T014 [US2] Extend the assistant-change command in `src/task_manager/domain/implementation.py` so a `consequential` request and an `ordinary` request with stop set satisfy `tests/unit/test_assistant_approval.py`. Store a consequential request as class `consequential` with `stopped` `0`. Store an ordinary request that stopped as class `consequential` with `stopped` `1`. Do not carry either out. Refuse `actor` `assistant` on approve and on decline before any resolution row is written, with `The assistant cannot approve a change.` and `The assistant cannot decline a change.` An omitted actor stays the engineer's existing approve and decline path.
- [X] T015 [US2] Pass `stopped` through `record_assistant_change` in `src/task_manager/workspace.py`, `POST /api/tasks/{id}/assistant-changes` in `src/task_manager/web/api.py`, and the assistant form in `src/task_manager/web/pages.py` and `src/task_manager/web/templates/detail.html`. Pass `actor` through the existing approve and decline routes in `src/task_manager/web/api.py`. The page does not offer approve or decline to the assistant.

**Checkpoint**: User Stories 1 and 2 work — an ordinary change is Carried out, and a consequential or stopped request waits for the engineer

---

## Phase 5: User Story 3 - Leave a record that can be read again (Priority: P3)

**Goal**: The stored assistant change is what a later reader and a later replay use. The engineer's own change command still stores no assistant. A subtask change stays on the subtask. The assistant does not check, decide, or complete the task.

**Independent Test**: Carry out one ordinary assistant change, read it back, and run that same stored command script again from an empty workspace. The second pass shows the same account, assistant, project, and outcome, and does not carry the work out again.

### Tests for User Story 3 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T016 [P] [US3] Add failing unit tests in `tests/unit/test_assistant_record.py` for: `record` with a `project` and an `assistant_name` still stores an engineer change whose `project` is null, `assistant_name` is null, `recorded_by` is `engineer`, and `stopped` is false; an assistant change on a subtask appears on the subtask and does not appear on the parent; recording an assistant change does not insert a check or a decision; completing an otherwise legal task that has a carried-out assistant change with no passing check stays In Progress and includes `Needs a passing check:`; there is no domain function that updates or deletes an `assistant_change` row or calls a model.
- [X] T017 [P] [US3] Add failing contract tests in `tests/contract/test_assistant_record_api.py` for `POST /api/tasks/{id}/implementation-changes` with extra `project` and `assistant_name` fields. Assert they are ignored and the saved change has `recorded_by` `engineer`. Assert `GET /api/tasks/{id}` for a parent does not list a subtask's assistant change.

### Implementation for User Story 3

- [X] T018 [US3] Keep `record` in `src/task_manager/domain/implementation.py` and `POST /api/tasks/{id}/implementation-changes` in `src/task_manager/web/api.py` from writing `assistant_change`. Keep change lists in `src/task_manager/storage/implementation_store.py` filtered by that task's id so a subtask change is not copied onto the parent. Do not add a model call or a project write. Do not add a completion guard in `src/task_manager/domain/status.py`; the feature 003 guard already covers a carried-out assistant change.

**Checkpoint**: All three stories work — the stored account is the record, the engineer's command is unchanged, and completion still waits for a passing check

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Replay and the quickstart

- [X] T019 Extend `tests/integration/test_replay.py` so the same script — record one ordinary assistant change with project `billing` and account `Rename the export label` — run twice from an In Progress task with the same `ScriptedClock` and the same account, produces the same account, project, assistant name, Carried out outcome, and order, and does not call a model or write the project
- [X] T020 Run the three manual scenarios in `specs/005-assist-ordinary-change/quickstart.md` against a fresh `workspace.db` and fix any mismatch in `src/task_manager/` before treating the feature as done

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **User Stories (Phase 3–5)**: Depend on Foundational
- **Polish (Phase 6)**: Depends on the user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Foundational. No dependency on other stories
- **User Story 2 (P2)**: Starts after User Story 1, because it extends the same assistant-change command with consequential and stop
- **User Story 3 (P3)**: Starts after User Story 1, because it reads an assistant change that story records. It does not depend on User Story 2. The engineer-command and subtask rules are tested on their own in `tests/unit/test_assistant_record.py`

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Domain rules before the workspace method
- Workspace method before the HTTP route and the page
- Story checkpoint before the next story

### Parallel Opportunities

- T005 and T006 can run in parallel
- T012 and T013 can run in parallel
- T016 and T017 can run in parallel
- T003 and T004 stay sequential because both edit `src/task_manager/storage/implementation_store.py`
- Story phases that share `src/task_manager/domain/implementation.py`, `src/task_manager/web/api.py`, and `src/task_manager/web/templates/detail.html` stay sequential for those files
- T019 starts after those stories, because the replay script records an assistant change

---

## Parallel Example: User Story 1

```bash
# Write the failing User Story 1 tests together:
Task: "T005 tests/unit/test_assistant_change.py"
Task: "T006 tests/contract/test_assistant_change_api.py"

# Then implement in order: T007 domain, T008 workspace, T009 API, T010 pages, T011 assistant flag
```

## Parallel Example: User Story 2

```bash
Task: "T012 tests/unit/test_assistant_approval.py"
Task: "T013 tests/contract/test_assistant_approval_api.py"
```

## Parallel Example: User Story 3

```bash
Task: "T016 tests/unit/test_assistant_record.py"
Task: "T017 tests/contract/test_assistant_record_api.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Run `tests/unit/test_assistant_change.py` and `tests/contract/test_assistant_change_api.py`
5. Demo one ordinary assistant change before adding the approval stop

### Incremental Delivery

1. Setup + Foundational → assistant name and the assistant fields on each change
2. User Story 1 → record one ordinary assistant change (MVP)
3. User Story 2 → consequential and stopped requests wait for the engineer
4. User Story 3 → keep the engineer's command, the subtask boundary, and the stored record
5. Polish → replay test and quickstart scenarios

### Parallel Team Strategy

With multiple people:

1. Complete Setup and Foundational together
2. After that, one person owns User Story 1 through its checkpoint
3. User Story 2 then owns consequential, stop, and the assistant approve refusal in `src/task_manager/domain/implementation.py`
4. User Story 3 owns the proof that `record` stays an engineer change
5. Within a story, the failing tests can be written at the same time

---

## Notes

- [P] tasks = different files, no dependencies on incomplete work
- [US1]–[US3] map to the three stories in spec.md
- Verify each story's tests fail before implementing that story
- Do not call a model and do not write the named project
- Do not infer ordinary or consequential from the wording of the account
- Do not let the assistant approve or decline a change
- Do not refuse completion with a new sentence; a carried-out assistant change already needs a passing check
- Commit after each task or logical group
- Stop at any checkpoint to validate that story alone
