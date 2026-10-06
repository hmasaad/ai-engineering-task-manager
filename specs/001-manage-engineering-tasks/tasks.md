---
description: "Task list for Manage Engineering Tasks"
---

# Tasks: Manage Engineering Tasks

**Input**: Design documents from `/specs/001-manage-engineering-tasks/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Included. Constitution Principle II and plan.md require a failing test for each behavior before that behavior is implemented. A passing test that does not map to a spec scenario does not count.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested on its own.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/task_manager/`, `tests/` at repository root
- Paths follow plan.md: `src/task_manager/domain/`, `src/task_manager/storage/`, `src/task_manager/web/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and the package layout from plan.md

- [X] T001 Create `src/task_manager/__init__.py`, `src/task_manager/domain/__init__.py`, `src/task_manager/storage/__init__.py`, `src/task_manager/web/__init__.py`, and `tests/unit/__init__.py`, `tests/integration/__init__.py`, `tests/contract/__init__.py`
- [X] T002 [P] Create `pyproject.toml` requiring Python 3.12 and declaring fastapi, uvicorn, jinja2, and pytest, with the package rooted at `src/`
- [X] T003 [P] Implement `SystemClock` and `ScriptedClock` in `src/task_manager/clock.py` so tests can queue timestamps and production reads the system clock

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared workspace, schema, and process shell that every story uses

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 [P] Create `src/task_manager/storage/schema.sql` with tables `workspace`, `task`, `acceptance_criterion`, `status_change`, `implementation_decision`, and `decision_supersedes`. Enforce: `task.status` is exactly one of `Draft`, `Ready`, `In Progress`, `Completed`, `Cancelled`; `task.title` is non-empty; `task.parent_id` is null or another task id; `task.cancel_reason` is non-empty only when status is `Cancelled` and empty otherwise; a criterion is Verified only when `observation`, `pass_result`, `verified_at`, and `provider_name` are all present, and Unverified only when all four are absent; `pass_result` stores only `pass`; decisions and status changes have no delete path in the schema
- [X] T005 [P] Define refusal results in `src/task_manager/domain/results.py` with codes 400 (blank or wrong shape), 404 (missing id), and 409 (illegal for the current status or links), and a message string. A refusal must be returnable without writing rows
- [X] T006 Implement `src/task_manager/storage/connection.py` to open or create one SQLite file, enable foreign keys, apply `src/task_manager/storage/schema.sql`, seed `workspace.engineer_name` from configuration or `Engineer`, and run each later command in one transaction that rolls back when the domain returns a refusal
- [X] T007 Implement the process shell in `src/task_manager/web/app.py` and `src/task_manager/__main__.py` so `python -m task_manager --workspace ./workspace.db --engineer "Ada" --port 8000` binds to `127.0.0.1` only and stores the engineer name on the workspace without a login

**Checkpoint**: Foundation ready — user story implementation can now begin

---

## Phase 3: User Story 1 - Capture a task with a goal and acceptance criteria (Priority: P1) 🎯 MVP

**Goal**: An engineer creates a task, sets a goal, adds acceptance criteria, and marks it Ready only when the title, goal, and at least one criterion are present.

**Independent Test**: Create one task with a title, a goal, and two acceptance criteria, open it from the list, and confirm those fields are unchanged. Mark it Ready. A blank title creates nothing.

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T008 [P] [US1] Add failing unit tests in `tests/unit/test_capture_task.py` for: a blank or whitespace title is refused and creates nothing; a created task has status exactly `Draft`; duplicate titles are allowed and stay distinct; a new criterion is Unverified, meaning `observation`, `pass_result`, `verified_at`, and `provider_name` are all absent; `Draft` → `Ready` is refused unless title, goal, and at least one criterion are each non-empty; clearing the goal or removing the last criterion of a `Ready` task returns it to `Draft` with cause `goal_or_last_criterion_removed`
- [X] T009 [P] [US1] Add failing contract tests in `tests/contract/test_capture_api.py` for `POST /api/tasks`, `GET /api/tasks`, `GET /api/tasks/{id}`, `PATCH /api/tasks/{id}`, `POST/PATCH/DELETE /api/tasks/{id}/criteria`, and `POST /api/tasks/{id}/transitions` with action `mark_ready`, including the 400 and 409 error body `{"refused": true, "message": "..."}` from `specs/001-manage-engineering-tasks/contracts/http-api.md`
- [X] T010 [P] [US1] Add a failing integration test in `tests/integration/test_capture_flow.py` that lists top-level tasks oldest first by `created_at`, then `id`, and shows goal and Unverified criteria on the task detail

### Implementation for User Story 1

- [X] T011 [US1] Implement create, goal edit, criterion add/edit/remove, and mark-ready rules in `src/task_manager/domain/capture.py` so they satisfy the tests in `tests/unit/test_capture_task.py` and do not start, complete, cancel, verify, or add subtasks
- [X] T012 [US1] Persist tasks and criteria through `src/task_manager/storage/task_store.py`, assigning integer ids in creation order and trimming text before the empty check
- [X] T013 [US1] Expose the User Story 1 commands from `src/task_manager/web/api.py` using the paths and status codes in `specs/001-manage-engineering-tasks/contracts/http-api.md`
- [X] T014 [US1] Render the task list and task detail in `src/task_manager/web/pages.py`, `src/task_manager/web/templates/list.html`, and `src/task_manager/web/templates/detail.html` with create, goal, criterion, and mark-ready actions, showing a refusal message without changing stored rows

**Checkpoint**: User Story 1 is functional on its own — create, goal, criteria, Ready, and the list

---

## Phase 4: User Story 2 - Track status through to completion (Priority: P2)

**Goal**: An engineer starts a Ready task, verifies each criterion with an observation, an explicit pass, and a time, and completes it only when every criterion is Verified. Completed work can be reopened. Cancelled work cannot return.

**Independent Test**: On one Ready task with no subtasks, start it, verify each criterion, mark it completed, and read a history from Ready through In Progress to Completed. A completion attempt with an Unverified criterion does not change status.

### Tests for User Story 2 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T015 [P] [US2] Add failing unit tests in `tests/unit/test_status.py` covering only these transitions: `Ready` → `In Progress` (`started`); `In Progress` → `Completed` (`completed`) only when every criterion is Verified; `Ready` → `Completed` refused; verify only while `In Progress` by storing a non-empty observation, pass result `pass`, the clock time, and the workspace `engineer_name`; an observation without `pass` leaves the criterion Unverified and writes none of the four verification fields; unverify while `In Progress` clears those four fields and does not change status; editing Verified criterion text clears the four fields, and if the task was `Completed` it becomes `In Progress` with cause `criterion_text_edited`; reopen requires a non-empty reason, returns `Completed` → `In Progress` with cause `reopened`, and keeps verified criteria; every Completed ancestor also becomes `In Progress` with that same cause and keeps its own verified criteria; cancel requires a non-empty reason, sets `cancel_reason`, and is refused while a direct subtask is `Draft`, `Ready`, or `In Progress`; a `Cancelled` task has no outward transition and refuses goal edits, criterion edits, new criteria, and new verifications
- [X] T016 [P] [US2] Add failing contract tests in `tests/contract/test_status_api.py` for `POST /api/tasks/{id}/transitions` actions `start`, `complete`, `cancel`, and `reopen`, `POST /api/tasks/{id}/criteria/{criterion_id}/verify`, and `POST /api/tasks/{id}/criteria/{criterion_id}/unverify`, asserting the provider is the workspace engineer name and not a name from the request body

### Implementation for User Story 2

- [X] T017 [US2] Implement the status, verify, unverify, and criterion-text side effects in `src/task_manager/domain/status.py` so a refused command returns a 409 message naming unmet criteria and unfinished subtasks and leaves stored rows unchanged
- [X] T018 [US2] Append `status_change` rows and verification columns in `src/task_manager/storage/status_store.py`, ordered by `occurred_at` then `id`, using the cause codes `started`, `completed`, `cancelled`, `reopened`, and `criterion_text_edited`
- [X] T019 [US2] Add the status, verify, and unverify routes to `src/task_manager/web/api.py` per `specs/001-manage-engineering-tasks/contracts/http-api.md`
- [X] T020 [US2] Add start, complete, cancel, reopen, verify, and unverify actions to `src/task_manager/web/templates/detail.html`, and on a Cancelled task show the record with no mutating actions plus the message that continued work is a new task

**Checkpoint**: User Stories 1 and 2 both work — a task with no subtasks can be completed and reopened

---

## Phase 5: User Story 3 - Break a task into subtasks (Priority: P3)

**Goal**: An engineer adds subtasks. Each subtask is a task with one parent. A parent cannot be completed or cancelled while a direct subtask is still unfinished, and a task cannot contain its own ancestor.

**Independent Test**: Add two subtasks to one parent and confirm they appear in creation order. With the parent's own criteria Verified, completing the parent while one subtask is Ready leaves the parent In Progress and names that subtask.

### Tests for User Story 3 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T021 [P] [US3] Add failing unit tests in `tests/unit/test_subtasks.py` for: a subtask is a `Draft` task with exactly one `parent_id`; `parent_id` cannot be the task itself, a second parent, or a descendant; a new subtask is refused when the parent is `Completed` or `Cancelled`; children are ordered by `created_at` then `id`; `In Progress` → `Completed` is refused while any direct subtask is `Draft`, `Ready`, or `In Progress`, and the refusal names those subtasks; a `Completed` or `Cancelled` direct subtask does not block; the same completion rule applies at every level so an unfinished grandchild blocks its parent
- [X] T022 [P] [US3] Add failing contract tests in `tests/contract/test_subtasks_api.py` for `POST /api/tasks/{id}/subtasks` and for parent completion and parent cancel refusals in `specs/001-manage-engineering-tasks/contracts/http-api.md`

### Implementation for User Story 3

- [X] T023 [US3] Implement subtask creation and the parent completion and cancel guards in `src/task_manager/domain/subtasks.py`, walking ancestors to reject a cycle before the link is stored
- [X] T024 [US3] Store `parent_id` and list children in `src/task_manager/storage/subtask_store.py` with no command that moves a task onto a different parent
- [X] T025 [US3] Add `POST /api/tasks/{id}/subtasks` to `src/task_manager/web/api.py` and include subtask summaries `{id, title, status, created_at}` on the task detail
- [X] T026 [US3] Add the subtask form and child links to `src/task_manager/web/templates/detail.html` per `specs/001-manage-engineering-tasks/contracts/ui.md`

**Checkpoint**: User Stories 1–3 work — parents and nested subtasks follow one status rule

---

## Phase 6: User Story 4 - Record implementation decisions (Priority: P4)

**Goal**: An engineer records a decision with a statement and a rationale. A later decision can supersede one or more earlier decisions on the same task, and every named decision stays visible.

**Independent Test**: On one task, save two decisions, then save a third that supersedes both, and confirm all three remain visible and the third names the first two.

### Tests for User Story 4 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T027 [P] [US4] Add failing unit tests in `tests/unit/test_decisions.py` for: a decision requires a non-empty statement and a non-empty rationale and belongs to exactly one task; it may name zero or more earlier decisions on that same task; it is refused when it names itself, a decision recorded after it (`recorded_at`, then `id`), or a decision on another task, and nothing is saved; named decisions stay unchanged; there is no update or delete; a Cancelled task refuses a new decision
- [X] T028 [P] [US4] Add failing contract tests in `tests/contract/test_decisions_api.py` for `POST /api/tasks/{id}/decisions` with `supersedes`, asserting 400 for a blank rationale and 409 for another task's decision id, and that `GET /api/tasks/{id}` returns decisions oldest first

### Implementation for User Story 4

- [X] T029 [US4] Implement decision recording and supersede checks in `src/task_manager/domain/decisions.py` with no function that updates or deletes a decision
- [X] T030 [US4] Insert `implementation_decision` and `decision_supersedes` rows in `src/task_manager/storage/decision_store.py`
- [X] T031 [US4] Add `POST /api/tasks/{id}/decisions` to `src/task_manager/web/api.py` and return `supersedes` ids on the task detail from `specs/001-manage-engineering-tasks/contracts/http-api.md`
- [X] T032 [US4] Add the decision form to `src/task_manager/web/templates/detail.html`, listing each decision with its statement, rationale, time, and superseded ids

**Checkpoint**: All four user stories work on their own paths

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Replay, the quickstart, and checks that cut across stories

- [X] T033 [P] Add `tests/integration/test_replay.py` to run the same create, mark-ready, start, verify, complete, reopen, subtask, and decision script twice from empty workspaces with the same `ScriptedClock`, and assert the same statuses, verification states, and ordering
- [X] T034 [P] Add a test in `tests/contract/test_localhost.py` that the server settings in `src/task_manager/__main__.py` bind to `127.0.0.1` and do not accept a provider name from a verify request
- [X] T035 Run the four manual scenarios in `specs/001-manage-engineering-tasks/quickstart.md` against a fresh `workspace.db` and fix any mismatch in `src/task_manager/` before treating the feature as done

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **User Stories (Phase 3–6)**: Depend on Foundational
- **Polish (Phase 7)**: Depends on the user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Foundational. No dependency on other stories
- **User Story 2 (P2)**: Starts after User Story 1, because start, verify, and complete act on a task that can already become Ready
- **User Story 3 (P3)**: Starts after User Story 2, because parent completion and cancel use those status commands. Subtask rules are still tested on their own in `tests/unit/test_subtasks.py`
- **User Story 4 (P4)**: Starts after User Story 1 for a task to attach a decision to. The Cancelled refusal is tested after User Story 2 has cancellation

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Domain rules before storage
- Storage before HTTP routes
- Routes before the page that submits them
- Story checkpoint before the next story

### Parallel Opportunities

- T002 and T003 can run in parallel after T001
- T004 and T005 can run in parallel
- T008, T009, and T010 can run in parallel
- T015 and T016 can run in parallel
- T021 and T022 can run in parallel
- T027 and T028 can run in parallel
- T033 and T034 can run in parallel
- Story phases stay sequential because later stories extend `src/task_manager/web/api.py` and `src/task_manager/web/templates/detail.html`

---

## Parallel Example: User Story 1

```bash
# Write the failing User Story 1 tests together:
Task: "T008 tests/unit/test_capture_task.py"
Task: "T009 tests/contract/test_capture_api.py"
Task: "T010 tests/integration/test_capture_flow.py"

# Then implement in order: T011 domain, T012 storage, T013 API, T014 pages
```

## Parallel Example: User Story 2

```bash
Task: "T015 tests/unit/test_status.py"
Task: "T016 tests/contract/test_status_api.py"
```

## Parallel Example: User Story 3

```bash
Task: "T021 tests/unit/test_subtasks.py"
Task: "T022 tests/contract/test_subtasks_api.py"
```

## Parallel Example: User Story 4

```bash
Task: "T027 tests/unit/test_decisions.py"
Task: "T028 tests/contract/test_decisions_api.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Run `tests/unit/test_capture_task.py`, `tests/contract/test_capture_api.py`, and `tests/integration/test_capture_flow.py`
5. Demo the list and a Ready task before starting status transitions

### Incremental Delivery

1. Setup + Foundational → empty workspace process
2. User Story 1 → tasks with goals and criteria (MVP)
3. User Story 2 → start, verify, complete, reopen, cancel
4. User Story 3 → subtasks and parent guards
5. User Story 4 → decisions that can supersede several earlier decisions
6. Polish → replay test and quickstart scenarios

### Parallel Team Strategy

With multiple people:

1. Complete Setup and Foundational together
2. After that, one person owns User Story 1 through its checkpoint
3. The next stories follow in order because they share `src/task_manager/web/api.py` and `src/task_manager/web/templates/detail.html`
4. Within a story, the failing tests can be written at the same time

---

## Notes

- [P] tasks = different files, no dependencies on incomplete work
- [US1]–[US4] map to the four stories in spec.md
- Verify each story's tests fail before implementing that story
- Do not infer completion from a goal, a decision, or a criterion existing
- Commit after each task or logical group
- Stop at any checkpoint to validate that story alone
