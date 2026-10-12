---
description: "Task list for Trace Requirements"
---

# Tasks: Trace Requirements

**Input**: Design documents from `/specs/009-trace-requirements/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Included. The specification (FR-014) and Constitution Principle II require a failing automated check before each behavior. Unit tests cover one rule. The integration test covers the path from a requirement through a task and a criterion to a stored run.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested on its own.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Setup and foundational tasks have no story label

## Path Conventions

- Application code: `src/task_manager/`
- Tests: `tests/unit/`, `tests/contract/`, `tests/integration/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add the stored tables this feature needs. No new dependency and no change to existing tables.

- [X] T001 Add `requirement`, `requirement_task`, `requirement_criterion`, `requirement_check`, and `verification_run` to `src/task_manager/storage/schema.sql` with `CREATE TABLE IF NOT EXISTS` only. `requirement.kind` is `functional` or `non-functional`. `requirement.statement` is non-empty after trimming. `requirement_task` primary key is `(requirement_id, task_id)` and it has an index on `task_id`. `requirement_criterion.criterion_id` references `acceptance_criterion(id)` with `ON DELETE CASCADE`. `requirement_check.name` is non-empty after trimming, `removed_at` is null while the check is still named, and a unique index on `(requirement_id, name)` applies only where `removed_at` is null. `verification_run` is insert-only: `result` is `passed` or `failed`, and `run_identifier` is non-empty after trimming. Do not alter `task`, `acceptance_criterion`, `implementation_check`, or `implementation_change`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: One store module every story reads and writes. No user story starts before this exists.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T002 Add `src/task_manager/storage/requirement_store.py` to insert and fetch a requirement. Store the trimmed statement and reject a blank one. Store only `functional` or `non-functional`. Assign `id` at insert and expose it as `REQ-{id}`. Do not update, delete, link, name a check, or record a run in this task.

**Checkpoint**: A requirement row can be stored and read back with a stable `REQ-` identifier.

---

## Phase 3: User Story 1 - Give a requirement a stable identity and a trace (Priority: P1) 🎯 MVP

**Goal**: The engineer records a functional or non-functional requirement, links it to a task and to a criterion on that task, and reads the identifier back. A task with no linked requirement still completes under the existing rules.

**Independent Test**: Create one functional requirement, link it to one task and one criterion, and read `REQ-1` on the requirement and on the task. Complete a different task that has no requirement link.

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T003 [P] [US1] Add failing unit tests in `tests/unit/test_requirement.py` for a new `REQ-` identifier, a different identifier for a second requirement, blank statement `A requirement statement is required.`, unknown kind `Choose functional or non-functional.`, unknown requirement `Requirement not found.`, unknown task `Task not found.`, a criterion from another task or a task that is not linked `The criterion must be on that task.`, a duplicate criterion link `That criterion is already linked to this requirement.`, a duplicate task link that writes no second row, and a task with no linked requirement that still completes under the existing rules.
- [X] T004 [P] [US1] Add failing contract tests in `tests/contract/test_requirement_api.py` for `POST /api/requirements`, `POST /api/requirements/{id}/tasks`, `POST /api/requirements/{id}/criteria`, both unlink commands, and `requirements` on `GET /api/tasks/{id}`, using the status codes and messages in `specs/009-trace-requirements/contracts/http-api.md`. A wrong-shaped body is 400 `The request is missing a required field or has the wrong shape.`

### Implementation for User Story 1

- [X] T005 [US1] Implement record, link task, link criterion, and unlink in `src/task_manager/domain/requirement.py` and the matching functions in `src/task_manager/storage/requirement_store.py`. Follow the validation order in `specs/009-trace-requirements/data-model.md`. Linking does not change task status. Unlinking does not change Verified state. Deleting a criterion through `src/task_manager/domain/capture.py` removes only the criterion link.
- [X] T006 [US1] Add the User Story 1 commands to `src/task_manager/workspace.py`, `src/task_manager/web/api.py`, and `src/task_manager/web/pages.py`. Ignore a client-supplied engineer name and time.
- [X] T007 [US1] Add `requirements` to the task detail in `src/task_manager/storage/task_store.py`. It is an empty list when the task has no link. Each item has `id`, `identifier`, `kind`, and `statement`. A subtask's links do not appear on the parent.
- [X] T008 [US1] Add the requirements list, the requirement page, and the task-detail identifier line in `src/task_manager/web/templates/requirements.html`, `src/task_manager/web/templates/requirement.html`, `src/task_manager/web/templates/detail.html`, and the requirements link in `src/task_manager/web/templates/base.html`, matching `specs/009-trace-requirements/contracts/ui.md`.

**Checkpoint**: User Story 1 works alone. A task with no requirement link still completes as it does today.

---

## Phase 4: User Story 2 - Record a run and hold verification until required checks pass (Priority: P2)

**Goal**: The engineer names a check, records Passed or Failed with a run identifier, and cannot verify a linked criterion or complete a linked task while a still-named check is not currently Passed.

**Independent Test**: Name one check, record Failed, and confirm verification and completion are refused. Record a later Passed run and confirm that run is current, the earlier run remains, and the existing verify and complete steps can proceed.

### Tests for User Story 2 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T009 [P] [US2] Add failing unit tests in `tests/unit/test_requirement_run.py` for naming a check, a duplicate active name `That check is already named on this requirement.`, a blank name `Name the check this requirement uses.`, a run that stores the workspace engineer and the clock time, a later Failed run becoming current while the earlier run remains, a blank run identifier `A run identifier is required.`, a bad result `Choose Passed or Failed.`, an unknown or retired check `Check not found.`, verify refused with `A required check has not passed.` when the current result is Failed or missing, a criterion with no linked requirement still becoming Verified, completion appending `A required check has not passed: REQ-1` after the existing sentences, removal keeping runs and ending the hold, the same name added again starting with no current result, and a requirement linked only to a subtask refuses that subtask with `A required check has not passed: REQ-1` and leaves that identifier out of the parent's completion message.
- [X] T010 [P] [US2] Add failing contract tests in `tests/contract/test_requirement_run_api.py` for `POST /api/requirements/{id}/checks`, `POST /api/requirements/{id}/checks/{check_id}/remove`, and `POST /api/requirements/{id}/runs`, including the refusal order requirement, then check name, then run identifier, then result.

### Implementation for User Story 2

- [X] T011 [US2] Implement name, remove, and record-run in `src/task_manager/domain/requirement.py` and `src/task_manager/storage/requirement_store.py`. Store the trimmed check name and the trimmed run identifier. `result` is stored as `passed` or `failed` and shown as Passed or Failed. Removal sets `removed_at` and does not delete runs. The current result is the latest run by `recorded_at`, then `id`. A run does not change task status, criterion state, a change outcome, or a feature 003 check.
- [X] T012 [US2] After the existing feature 001 checks in `src/task_manager/domain/capture.py`, refuse verification with `A required check has not passed.` when any requirement linked to that criterion has an active check whose current result is not Passed. Write no verification in that case.
- [X] T013 [US2] In `src/task_manager/domain/status.py`, keep the existing completion sentences first and append `A required check has not passed: {identifiers}.` Identifiers are `REQ-{id}`, lowest id first, separated by a comma and a space. A requirement with no active check adds nothing. A task with no linked requirement keeps today's message exactly.
- [X] T014 [US2] Add the check and run commands to `src/task_manager/workspace.py`, `src/task_manager/web/api.py`, `src/task_manager/web/pages.py`, and the forms on `src/task_manager/web/templates/requirement.html`.

**Checkpoint**: User Stories 1 and 2 both work. Recording a run does not by itself verify a criterion or complete a task.

---

## Phase 5: User Story 3 - Find requirements that are not traced or not verified (Priority: P3)

**Goal**: One list shows requirements missing a task, a criterion, a named check, or a current pass. A fully traced requirement whose every named check is Passed does not appear. Old tasks and criteria are not listed as requirements.

**Independent Test**: Four requirements: one unlinked, one linked to a task only, one with a named check and no pass, and one fully traced and Passed. Only the first three appear.

### Tests for User Story 3 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T015 [P] [US3] Add failing unit tests in `tests/unit/test_requirement_gaps.py` for `Missing a task`, `Missing an acceptance criterion`, `Missing a check`, and `Missing a passing result for {check name}`, in that order, including one passing phrase per active check that is not currently Passed. A complete requirement is absent. Tasks that are not requirements do not appear.

### Implementation for User Story 3

- [X] T016 [US3] Return `missing` from `GET /api/requirements` in `src/task_manager/storage/requirement_store.py` and `src/task_manager/web/api.py`. Show the gap list first, then every requirement, in `src/task_manager/web/templates/requirements.html`. An empty workspace says no requirements yet.

**Checkpoint**: The gap list matches the four-requirement independent test without changing completion for an unlinked task.

---

## Phase 6: User Story 4 - See what a requirement change affects (Priority: P4)

**Goal**: Changing the statement or the kind keeps the identifier, shows the linked tasks, criteria, and checks, and returns linked Verified criteria to Unverified. An unchanged save does nothing.

**Independent Test**: Link one requirement to one Verified criterion on a Completed task, save the same statement and kind, then change the statement. The first save leaves the task Completed. The second returns the criterion to Unverified, the task and its Completed parent to In Progress, and keeps the run.

### Tests for User Story 4 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T017 [P] [US4] Add failing unit tests in `tests/unit/test_requirement_change.py` for an unchanged trimmed statement and kind writing no criterion change, no status change, and no history row; a blank replacement refused with `A requirement statement is required.` and the stored row left unchanged; a different statement or kind clearing verification only on linked criteria, moving that Completed task and every Completed ancestor to In Progress once with cause `requirement_changed` and the requirement id, and leaving runs readable.

### Implementation for User Story 4

- [X] T018 [US4] Implement the requirement change in `src/task_manager/domain/requirement.py`. Reuse `_leave_completed` in `src/task_manager/domain/capture.py` with cause `requirement_changed`. Do not rewrite runs. Do not change criteria that are not linked to that requirement.
- [X] T019 [US4] Add `POST /api/requirements/{id}` in `src/task_manager/web/api.py` and `src/task_manager/web/pages.py`, and the save form on `src/task_manager/web/templates/requirement.html`. Show retired checks and their runs on that page.

**Checkpoint**: All four stories work. Specification 001 is not edited. The new history cause is `requirement_changed`.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: The full path and the manual quickstart.

- [X] T020 [P] Add `tests/integration/test_requirement_trace.py` that fails when the path from a requirement through its linked task and acceptance criterion to a stored run is broken. Opening the requirement does not record a run and does not mark a check Passed.
- [X] T021 Run the manual checks in `specs/009-trace-requirements/quickstart.md` against a fresh workspace.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on T001. Blocks every user story.
- **User Story 1 (Phase 3)**: Depends on Phase 2. No dependency on later stories.
- **User Story 2 (Phase 4)**: Depends on Phase 2 and on the links from User Story 1 for the verify and completion holds. Naming a check and recording a run can be tested on a requirement alone.
- **User Story 3 (Phase 5)**: Depends on Phase 2 and on requirements from User Story 1. The passing-result phrase depends on User Story 2.
- **User Story 4 (Phase 6)**: Depends on the links from User Story 1. A stored run from User Story 2 is needed only for the assertion that runs stay.
- **Polish (Phase 7)**: Depends on the stories being present.

### User Story Dependencies

- **User Story 1 (P1)**: Starts after T002. This is the MVP.
- **User Story 2 (P2)**: Starts after User Story 1 links exist. T012 and T013 both depend on T011. They edit different files and can be done in either order after T011.
- **User Story 3 (P3)**: Starts after requirements can be linked and checks can be recorded.
- **User Story 4 (P4)**: Starts after a requirement can be linked to a criterion. It does not change the run rules.

### Within Each User Story

- Tests are written and fail before that story's implementation.
- The store and domain commands come before the API and pages.
- A story is independently testable at its checkpoint.

### Parallel Opportunities

- T003 and T004 can run together.
- T009 and T010 can run together.
- T015, T017, and T020 touch different test files and can run together once the behavior they describe is specified.
- T012 and T013 edit different files and can be done in either order after T011.

---

## Parallel Example: User Story 1

```bash
# Failing tests together, before implementation:
Task: "Unit tests in tests/unit/test_requirement.py"
Task: "Contract tests in tests/contract/test_requirement_api.py"

# After the domain commands exist:
Task: "Task detail requirements in src/task_manager/storage/task_store.py"
Task: "Workspace commands in src/task_manager/workspace.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3.
3. Stop and validate: one requirement, one task link, one criterion link, and an unlinked task that still completes.

### Incremental Delivery

1. Setup and foundation.
2. User Story 1: identity and trace.
3. User Story 2: stored runs and the hold.
4. User Story 3: gap list.
5. User Story 4: impact of a real statement or kind change.
6. Polish: full-path test and the quickstart.

## Notes

- [P] tasks use different files and do not depend on an unfinished task.
- Do not commit unless the user asks.
- Do not rewrite specifications 001 through 008 or the constitution.
- The product stores the result the engineer records. It does not run the named check.
- The 200-millisecond goal in plan.md is a design constraint. Completion uses the index on `requirement_task.task_id`. No separate timing task is required.
