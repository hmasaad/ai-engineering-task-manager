---
description: "Task list for Link a Decision to Its Evidence"
---

# Tasks: Link a Decision to Its Evidence

**Input**: Design documents from `/specs/004-link-decision-evidence/`

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

**Purpose**: Add the stored link this feature needs. The Python package, clock, and process shell already exist.

- [X] T001 Add `decision_check` to `src/task_manager/storage/schema.sql` with `CREATE TABLE IF NOT EXISTS`, so an existing workspace file gains it when `src/task_manager/storage/connection.py` runs the script. Columns: `decision_id` required, the primary key, unique, and references `implementation_decision(id)`; `check_id` required, not unique, and references `implementation_check(id)`. At most one row per decision. Many rows may name one check. No update or delete statement for this table. Do not add a column to `implementation_decision`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Insert and read the link without story rules. Every story reads decisions through the existing task detail.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T002 Implement insert and read functions in `src/task_manager/storage/decision_store.py` for `decision_check`. Insert one row with `decision_id` and `check_id`. Read the `check_id` for one `decision_id`, or report that no row exists. Do not check task status, statement, rationale, or which task the check belongs to. Do not add a function that updates or deletes `decision_check` or `implementation_decision`.
- [X] T003 Add `check` to each item returned by `decisions` in `src/task_manager/storage/task_store.py`, using T002. `check` is `null` when that decision has no `decision_check` row. When a row exists, `check` is the named `implementation_check` joined to its `implementation_change`, not the latest check of that change and criterion. Fields: `id`, `change_id`, `what_changed`, `criterion_id`, `criterion_text`, `evidence`, `result`, `engineer_name`, `checked_at`. Map stored `passed` to `Passed` and stored `failed` to `Failed`. Keep `id`, `statement`, `rationale`, `recorded_at`, and `supersedes`. Leave feature 001, feature 002, and feature 003 fields unchanged. Decisions stay ordered by `recorded_at` ascending, then `id` ascending.

**Checkpoint**: Foundation ready — user story implementation can now begin

---

## Phase 3: User Story 1 - Record a decision that names its check (Priority: P1) 🎯 MVP

**Goal**: An engineer records a decision on a task that is not Cancelled by giving a statement, a rationale, and exactly one check on that task. The task shows the statement, the rationale, the time, the criterion wording, what changed, the evidence, and Passed or Failed. Status, change outcome, the check, and the criterion's Verified state do not change.

**Independent Test**: On one task that is not Cancelled, record a carried-out change and a check of that change, then record a decision that names that check, and read the decision back on the task. The task status, the change outcome, the check, and the criterion's verification state stay as they were.

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T004 [P] [US1] Add failing unit tests in `tests/unit/test_linked_decision.py` that call the domain function for a decision that names a check and assert: a blank or whitespace statement or rationale is refused with `Both a statement and a rationale are required.` and writes no decision row and no `decision_check` row; a missing check id is refused with `Choose the check this decision rests on.` and writes nothing; when the statement is blank and the check id is also missing, the refusal is `Both a statement and a rationale are required.`; a `Passed` check on an In Progress task stores the statement, the rationale, the scripted clock time, and one `decision_check` row for that check id, and the task detail `check` shows that check's `criterion_text`, `what_changed`, `evidence`, and `Passed`; a `Failed` check stores the same way and `check.result` is `Failed`; task status, change outcome, the named check's `evidence` and `result`, criterion Verified state, earlier decisions, and status history stay unchanged; a caller-supplied engineer name is ignored; Cancelled is refused with `Decisions cannot be added to a cancelled task.` before a blank statement is considered; a Completed task with a check already stored accepts the decision and stays Completed; Draft and Ready accept the decision when the named check is on that task; an unknown task id is refused with `Task not found.`; an unknown check id is refused with `Check not found.`; a check on another task is refused with `The decision must name a check on that task.`
- [X] T005 [P] [US1] Add failing contract tests in `tests/contract/test_linked_decision_api.py` for `POST /api/tasks/{id}/linked-decisions` and `GET /api/tasks/{id}` using the status codes and exact messages in `specs/004-link-decision-evidence/contracts/http-api.md`. Assert the new decision is last in `decisions`, its `check` matches the named check, and a body field `engineer_name` is ignored. Assert a refused command returns `{"refused": true, "message": "..."}` and leaves the task status, the change outcome, and the check unchanged. Assert a wrong-shaped body is 400 with `The request is missing a required field or has the wrong shape.`

### Implementation for User Story 1

- [X] T006 [US1] Implement the linked-decision command in `src/task_manager/domain/decisions.py` so it satisfies `tests/unit/test_linked_decision.py`. Consider the task, then Cancelled, then the statement and rationale, then the check. Accept a check whose stored result is `passed` or `failed`. Insert the `implementation_decision` row and the `decision_check` row in the same command through `src/task_manager/storage/decision_store.py`. Return the task detail. Do not accept a supersede list in this task. Do not verify or unverify a criterion, record a check, approve a change, or change task status. Leave `add_decision` unchanged.
- [X] T007 [US1] Add `add_linked_decision` to `src/task_manager/workspace.py` so it runs that domain function inside the existing transaction and clock.
- [X] T008 [US1] Add `POST /api/tasks/{id}/linked-decisions` to `src/task_manager/web/api.py` with body fields `statement`, `rationale`, and `check_id`. Ignore extra fields, including `engineer_name`. Return the task detail or the refusal from `specs/004-link-decision-evidence/contracts/http-api.md`.
- [X] T009 [US1] Show `check` on each decision, and add the linked-decision form, on `src/task_manager/web/templates/detail.html`. Accept the form in `src/task_manager/web/pages.py` at `POST /tasks/{task_id}/linked-decisions`. Show the form only when the task is not Cancelled. The form asks for a statement, a rationale, and a check from this task, and includes an empty check choice. A decision with a check shows the criterion wording, the account of what changed, the evidence, and Passed or Failed. A refusal redisplays the detail with the API message and the same stored task. A success redisplays the detail without changing the status, the change outcome, or the check result. A Cancelled task shows its decisions and does not offer the form.

**Checkpoint**: User Story 1 is functional on its own — record a decision naming one check and read the chain back on that task

---

## Phase 4: User Story 2 - Keep the decision on the check it named (Priority: P2)

**Goal**: A later check of the same change and criterion does not rewrite a decision. The decision keeps the evidence and the result of the check it named.

**Independent Test**: Record a decision naming a Failed check, then record a later Passed check of the same change and criterion, and read the decision again. It still shows the earlier evidence and Failed. The later check is also still listed.

### Tests for User Story 2 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T010 [P] [US2] Add failing unit tests in `tests/unit/test_linked_decision_history.py` for: a decision that names a `Failed` check still shows that check's `evidence` and `Failed` after a later `Passed` check of the same change and criterion; the earlier check row is unchanged and the later check is listed after it; a check of a different criterion on the same change does not change the decision's `check.id`, `criterion_text`, `evidence`, or `result`; editing the live criterion text does not change `criterion_text` on the decision's `check`; removing the criterion does not delete the decision or the check, and the decision still shows the wording stored on the check; there is no domain function that updates or deletes a decision or a `decision_check` row.
- [X] T011 [P] [US2] Add failing contract tests in `tests/contract/test_linked_decision_history_api.py` for a linked decision followed by a later `POST /api/tasks/{id}/implementation-changes/{change_id}/checks` on the same pair. Assert `GET /api/tasks/{id}` leaves that decision's `check.id`, `check.evidence`, and `check.result` unchanged, and that both checks remain in `checks` in order. Assert no request can edit or delete the decision.

### Implementation for User Story 2

- [X] T012 [US2] Keep the decision read in `src/task_manager/storage/task_store.py` pointed at `decision_check.check_id` so it satisfies `tests/unit/test_linked_decision_history.py`. Do not replace that check with the latest `implementation_check` of the same `change_id` and `criterion_id`. Do not rewrite `criterion_text`, `evidence`, or `result` on the named check when a later check is inserted or when the live criterion text changes. Leave `src/task_manager/storage/decision_store.py` insert-only.

**Checkpoint**: User Stories 1 and 2 work — a later check stays in the check list and the decision still cites the earlier evidence and result

---

## Phase 5: User Story 3 - Supersede a decision without losing the chain (Priority: P3)

**Goal**: A later decision that names a check can supersede earlier decisions on the same task, including a decision that names no check. The existing decision command still saves a decision with no check. A subtask decision stays on the subtask. Completion and cancellation do not gain a new refusal.

**Independent Test**: On one task, save a decision that does not name a check, then save a decision that names a check and supersedes the first. Both remain visible, and only the second shows a check.

### Tests for User Story 3 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T013 [P] [US3] Add failing unit tests in `tests/unit/test_linked_decision_supersede.py` for: a linked decision that supersedes one earlier unlinked decision leaves both visible, oldest first, the later `supersedes` list contains the earlier id, and only the later decision has a non-null `check`; superseding two earlier decisions records both ids; a superseded decision on another task is refused with `A decision can only supersede earlier decisions on the same task.` and writes no new row; an unknown superseded id is refused with `Decision not found.`; a self id or a later decision is refused with `A decision cannot supersede itself or a decision that comes after it.`; `add_decision` with only a statement and a rationale still saves a decision whose `check` is `null`; a `check_id` passed to `add_decision` does not create a `decision_check` row; a linked decision on a subtask appears on the subtask and does not appear on the parent; completing and cancelling an otherwise legal task still succeed when a carried-out change has a passing check and no decision, and the completion message does not gain a sentence about a missing decision.
- [X] T014 [P] [US3] Add failing contract tests in `tests/contract/test_linked_decision_supersede_api.py` for `POST /api/tasks/{id}/linked-decisions` with `supersedes`, and for `POST /api/tasks/{id}/decisions`. Assert the status codes and exact messages in `specs/004-link-decision-evidence/contracts/http-api.md`. Assert a `check_id` on `POST /api/tasks/{id}/decisions` is ignored, the saved decision has `check` null, and `complete` is unchanged when no decision names a check.

### Implementation for User Story 3

- [X] T015 [US3] Extend the linked-decision command in `src/task_manager/domain/decisions.py` so it accepts `supersedes` and satisfies `tests/unit/test_linked_decision_supersede.py`. Reuse the feature 001 rules: a named decision must be an earlier decision on the same task, and each named decision stays unchanged. Write `decision_supersedes` in the same command as the decision and the `decision_check` row. A refusal writes none of those rows. Do not change `add_decision` so that it requires or stores a check.
- [X] T016 [US3] Pass `supersedes` through `add_linked_decision` in `src/task_manager/workspace.py`, `POST /api/tasks/{id}/linked-decisions` in `src/task_manager/web/api.py`, and the linked-decision form in `src/task_manager/web/pages.py` and `src/task_manager/web/templates/detail.html`. The form's supersede list may name earlier decisions on this task only. Keep `POST /api/tasks/{id}/decisions` and `POST /tasks/{task_id}/decisions` from storing a check. Do not list a subtask's decisions on the parent. Do not add a completion or cancellation guard in `src/task_manager/domain/status.py`.

**Checkpoint**: All three stories work — linked and unlinked decisions share one list, a later decision can supersede an earlier one, and completion is unchanged

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Replay and the quickstart

- [X] T017 Extend `tests/integration/test_replay.py` so the same script — record a decision naming one `Failed` check, then record a `Passed` check of that same change and criterion — run twice from a task with that one `Failed` check and no decision naming it, using the same `ScriptedClock`, produces the same statement, the same named check id, the same evidence and `Failed` result on that decision, and the same order
- [X] T018 Run the three manual scenarios in `specs/004-link-decision-evidence/quickstart.md` against a fresh `workspace.db` and fix any mismatch in `src/task_manager/` before treating the feature as done

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **User Stories (Phase 3–5)**: Depend on Foundational
- **Polish (Phase 6)**: Depends on the user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Foundational. No dependency on other stories
- **User Story 2 (P2)**: Starts after User Story 1, because it reads a decision that story records and then adds a later check
- **User Story 3 (P3)**: Starts after User Story 1, because it extends the same linked-decision command with `supersedes`. It does not depend on User Story 2. The supersede rules are tested on their own in `tests/unit/test_linked_decision_supersede.py`

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Domain rules before the workspace method
- Workspace method before the HTTP route and the page
- Story checkpoint before the next story

### Parallel Opportunities

- T004 and T005 can run in parallel
- T010 and T011 can run in parallel
- T013 and T014 can run in parallel
- Story phases that share `src/task_manager/domain/decisions.py`, `src/task_manager/storage/task_store.py`, `src/task_manager/web/api.py`, and `src/task_manager/web/templates/detail.html` stay sequential for those files
- T017 starts after those stories, because the replay script records a linked decision and a later check

---

## Parallel Example: User Story 1

```bash
# Write the failing User Story 1 tests together:
Task: "T004 tests/unit/test_linked_decision.py"
Task: "T005 tests/contract/test_linked_decision_api.py"

# Then implement in order: T006 domain, T007 workspace, T008 API, T009 pages
```

## Parallel Example: User Story 2

```bash
Task: "T010 tests/unit/test_linked_decision_history.py"
Task: "T011 tests/contract/test_linked_decision_history_api.py"
```

## Parallel Example: User Story 3

```bash
Task: "T013 tests/unit/test_linked_decision_supersede.py"
Task: "T014 tests/contract/test_linked_decision_supersede_api.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Run `tests/unit/test_linked_decision.py` and `tests/contract/test_linked_decision_api.py`
5. Demo a decision that names one check before adding history and supersede

### Incremental Delivery

1. Setup + Foundational → link table and `check` on each decision
2. User Story 1 → record a decision that names a check (MVP)
3. User Story 2 → keep that decision on the named check after a later check
4. User Story 3 → supersede, keep the unlinked decision command, and leave completion unchanged
5. Polish → replay test and quickstart scenarios

### Parallel Team Strategy

With multiple people:

1. Complete Setup and Foundational together
2. After that, one person owns User Story 1 through its checkpoint
3. User Story 2 and User Story 3 can then be split only where they do not edit the same function at the same time. User Story 2 owns the decision read in `src/task_manager/storage/task_store.py`. User Story 3 owns `supersedes` on the linked-decision command
4. Within a story, the failing tests can be written at the same time

---

## Notes

- [P] tasks = different files, no dependencies on incomplete work
- [US1]–[US3] map to the three stories in spec.md
- Verify each story's tests fail before implementing that story
- Do not infer a decision from a Passed check, a Failed check, or a Verified criterion
- Do not move a decision onto a later check of the same change and criterion
- Do not refuse completion or cancellation because a change has no decision
- Commit after each task or logical group
- Stop at any checkpoint to validate that story alone
