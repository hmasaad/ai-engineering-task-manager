---
description: "Task list for Verification Evidence and Trace Gaps"
---

# Tasks: Verification Evidence and Trace Gaps

**Input**: Design documents from `/specs/018-verification-evidence/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Included. The spec says the rules are covered by automated checks. Constitution Principle II requires a failing test before the behavior exists.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested on its own.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- Single project: `src/task_manager/`, `tests/` at the repository root

## Phase 1: Setup

**Purpose**: The evidence table. `acceptance_criterion` is not altered.

- [X] T001 Add `criterion_evidence` to `src/task_manager/storage/schema.sql` with `CREATE TABLE IF NOT EXISTS` only. `criterion_id` is the primary key and references `acceptance_criterion(id)` with `ON DELETE CASCADE`. `method` is required and `length(trim(method)) > 0`. `run_identifier` is required and `length(trim(run_identifier)) > 0`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: A criterion can be read with the evidence fields before the new checks exist.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T002 In `src/task_manager/storage/task_store.py`, left join `criterion_evidence` when reading a task's criteria. The payload adds `method` and `run_identifier`, both null when the criterion is Unverified or when no evidence row exists. `clear_verification` deletes the evidence row in the same command that clears the existing verification columns.

**Checkpoint**: An Unverified criterion reads `method` and `run_identifier` as null. Verification still accepts the existing observation and pass.

---

## Phase 3: User Story 1 - Record how a criterion was verified (Priority: P1) 🎯 MVP

**Goal**: Verifying a criterion stores the method and the test-run identifier with the observation, the pass, the time, and the workspace engineer. A blank method or a blank identifier stores nothing.

**Independent Test**: Verify one criterion with method `inspection` and test-run identifier `local-1`. The criterion shows both. A blank method leaves it Unverified and says `A verification method is required.`

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T003 [P] [US1] Add failing unit tests in `tests/unit/test_criterion_evidence.py` for a stored method and test-run identifier, trimmed spaces, opening the task without a rewrite, a later start with another engineer that does not rewrite them, a blank method `A verification method is required.`, a blank identifier `A test-run identifier is required.`, existing refusals that stay first, and unverify, edited text, and a changed requirement that clear both fields.

- [X] T004 [P] [US1] Add failing contract tests in `tests/contract/test_criterion_evidence_api.py` for `POST /api/tasks/{id}/criteria/{criterion_id}/verify`. A missing method is 400 `A verification method is required.` A missing identifier is 400 `A test-run identifier is required.` A task that is not In Progress is 409 `A criterion can be verified only while the task is In Progress.` before the method message. A client-supplied engineer name is ignored. Success returns the trimmed method and identifier.

### Implementation for User Story 1

- [X] T005 [US1] In `src/task_manager/domain/capture.py`, refuse a blank method and then a blank test-run identifier after the existing verification checks. Write `criterion_evidence` only after those checks pass, in the same command as the existing verification. Pass the two fields from `src/task_manager/workspace.py`, `src/task_manager/web/api.py`, and `src/task_manager/web/pages.py`.

- [X] T006 [US1] Show the method and the test-run identifier on a verified criterion in `src/task_manager/web/templates/detail.html`, and add `method-{id}` and `run-{id}` to the verify form.

**Checkpoint**: User Story 1 works. A new verification requires both fields. Older completion rules are unchanged.

---

## Phase 4: User Story 2 - See tasks and criteria the requirement list misses (Priority: P2)

**Goal**: The gap analysis lists every task with no linked requirement and every Unverified criterion. `GET /api/requirements` stays a list of requirements.

**Independent Test**: Create one task with one unverified criterion and no requirement. The analysis lists that task and that criterion. Linking the task and verifying the criterion removes each from its list.

### Tests for User Story 2 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T007 [P] [US2] Add failing unit tests in `tests/unit/test_traceability.py` for a task with no requirement, a subtask whose parent is linked, an Unverified criterion, a linked task that stays off the task list while its criterion is unverified, a cancelled task, and a requirement whose missing phrases stay `Missing a task`, `Missing an acceptance criterion`, and `Missing a check`.

- [X] T008 [P] [US2] Add failing contract tests in `tests/contract/test_traceability_api.py` for `GET /api/traceability`. `GET /api/requirements` stays a list and does not contain the unlinked task.

### Implementation for User Story 2

- [X] T009 [US2] Add the trace read in `src/task_manager/storage/requirement_store.py` and `src/task_manager/workspace.py`. Tasks are ordered by id. Criteria that are not Verified under the existing rule are ordered by id. Reading the lists does not write a row.

- [X] T010 [US2] Add `GET /api/traceability` in `src/task_manager/web/api.py` and the two sections in `src/task_manager/web/templates/requirements.html`, rendered from `src/task_manager/web/pages.py`. Headings are `Tasks without a requirement` and `Criteria without verification`. Show a section only when its list is not empty. Keep `No requirements yet.` when no requirement exists.

**Checkpoint**: User Stories 1 and 2 both work. The requirement gap phrases are unchanged.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Earlier verifications still succeed, and the full suite stays green.

- [X] T011 Pass a method and a test-run identifier from every existing `verify_criterion` call and every existing verify request in `tests/`, so those tests still record a verification.

- [X] T012 Run the full pytest suite and confirm `GET /api/requirements` remains a list.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS user stories
- **User Story 1 (Phase 3)**: Depends on Foundational
- **User Story 2 (Phase 4)**: Depends on Foundational. It does not depend on the new verification fields
- **Polish (Phase 5)**: Depends on User Story 1, because existing verify calls must send the new fields

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational. No dependency on User Story 2
- **User Story 2 (P2)**: Can start after Foundational. Independently testable with the existing Unverified state

### Parallel Opportunities

- T003 and T004 can run in parallel
- T007 and T008 can run in parallel
- User Story 2 tests can be written while User Story 1 tests are written

---

## Parallel Example: User Story 1

```bash
# Launch the User Story 1 tests together:
Task: "Unit tests in tests/unit/test_criterion_evidence.py"
Task: "Contract tests in tests/contract/test_criterion_evidence_api.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Stop and validate the verification record on its own

### Incremental Delivery

1. Setup and Foundational
2. User Story 1 → a criterion verification shows the method and the test-run identifier
3. User Story 2 → the gap analysis shows tasks and unverified criteria
4. Polish → the full suite stays green

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to the user story
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Avoid: changing requirement phrases, changing task statuses, or wrapping `GET /api/requirements` in an object
