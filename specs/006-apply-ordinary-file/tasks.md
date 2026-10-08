---
description: "Task list for Apply an Ordinary File"
---

# Tasks: Apply an Ordinary File

**Input**: Design documents from `/specs/006-apply-ordinary-file/`

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
- A test that writes a file passes a temporary directory as the workspace startup folder. The suite must not write into the repository.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add the stored table this feature needs. The Python package, clock, assistant name, and process shell already exist.

- [X] T001 Add `applied_file` to `src/task_manager/storage/schema.sql` with `CREATE TABLE IF NOT EXISTS`, so an existing workspace file gains it when `src/task_manager/storage/connection.py` runs the script. `change_id` is required, the primary key, unique, and references `implementation_change(id)`. `file_path` is required and non-empty after trimming. `was_new` is required and exactly `0` or `1`. `previous_text` is absent exactly when `was_new` is `1`, and present, possibly empty, when `was_new` is `0`. `file_text` is required and may be empty. At most one row per change. No update or delete statement for `applied_file`. Do not add a column to `assistant_change` or `implementation_change`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Remember the startup folder and attach one file row to a change. Every story reads changes through the existing task detail.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T002 Capture the startup folder when `Workspace` opens in `src/task_manager/workspace.py`. Default it to the process directory at construction. A caller, including a test, may pass another directory. Do not store that directory in SQLite. A later change to the process directory must not move it for an already open workspace. Do not resolve a project path in this task.
- [X] T003 Implement insert and read functions in `src/task_manager/storage/implementation_store.py` for `applied_file`. Insert one row with `change_id`, trimmed `file_path`, `was_new` of `0` or `1`, `previous_text` absent exactly when `was_new` is `1`, and `file_text` which may be empty. Read that row for one change id, or report that no row exists. Do not check task status, class, or the filesystem. Do not add a function that updates or deletes `applied_file`, `assistant_change`, or `implementation_change`.
- [X] T004 Add `file` to each change returned by `change_payload` in `src/task_manager/storage/implementation_store.py`, using T003. When no `applied_file` row exists, `file` is null. When a row exists, `file` is an object with `path` from `file_path`, `was_new` true only when the stored value is `1`, `previous_text` null when `was_new` is `1` and the stored text otherwise, and `text` from `file_text`. Leave feature 002 through feature 005 fields unchanged.

**Checkpoint**: Foundation ready — user story implementation can now begin

---

## Phase 3: User Story 1 - Write one new file (Priority: P1) 🎯 MVP

**Goal**: An engineer asks the assistant to write one new ordinary file for an In Progress task in an existing project folder. The file is created with the submitted text. The task shows the file, that it was new, the text, the project path, the assistant, and Carried out. The task stays In Progress.

**Independent Test**: On one In Progress task, point at an existing project folder and ask the assistant to add one new ordinary file. The file is in the project with the submitted text, the task shows that file and Carried out, and the task stays In Progress.

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T005 [P] [US1] Add failing unit tests in `tests/unit/test_applied_file.py` that pass a temporary startup folder into `Workspace` and call the assistant-file command. Assert: a blank or whitespace project is refused with `Name the project this change is for.` and writes no row and no file; a project path that is missing or is not a folder is refused with `The project must already exist.` and writes nothing; a blank or whitespace account is refused with `An account of what changed is required.` and writes nothing; when the project and the file name are both blank, the refusal is `Name the project this change is for.`; a missing class, or a class other than `ordinary` or `consequential`, is refused with `Choose ordinary or consequential.` and writes nothing; a blank or whitespace file name is refused with `Name the file this change writes.` and writes nothing; an absolute file path or a file path that climbs out of the project is refused with `The file must stay inside the named project.` and writes nothing outside the project; a missing destination folder is refused with `The folder for that file must already exist.` and does not create that folder; an ordinary request for a new file `notes/label.txt` with text `Export` in an existing project folder `billing` creates that file containing exactly `Export`, stores `class` `ordinary`, outcome Carried out, `project` `billing` as typed, `file.path` `notes/label.txt`, `file.was_new` true, `file.previous_text` null, `file.text` `Export`, `assistant_name` `Guide` rather than a name from the caller, `recorded_by` `assistant`, `stopped` false, and `engineer_name` `Ada`; an empty submitted text creates an empty file and still requires the account; task status, criterion Verified state, checks, decisions, and status history stay unchanged; Draft is refused with `The task must be In Progress.`; Ready is refused with `Start the task first.`; Completed is refused with `Reopen the task first.`; Cancelled is refused with `A cancelled task cannot be changed. Continued work is a new task.`; a wrong status is refused before a blank project, a blank account, or a blank file name; an unknown task id is refused with `Task not found.`
- [X] T006 [P] [US1] Add failing contract tests in `tests/contract/test_applied_file_api.py` for `POST /api/tasks/{id}/assistant-changes` and `GET /api/tasks/{id}` using the status codes and exact messages in `specs/006-apply-ordinary-file/contracts/http-api.md`. Use a temporary startup folder that already contains `billing/notes`. Assert the new change is last in `implementation_changes`, `file.text` is the submitted text, and body fields `assistant_name` and `engineer_name` are ignored. Assert a refused command returns `{"refused": true, "message": "..."}` and leaves the task status and the project folder unchanged. Assert a wrong-shaped body is 400 with `The request is missing a required field or has the wrong shape.`

### Implementation for User Story 1

- [X] T007 [US1] Implement the ordinary new-file path in `src/task_manager/domain/implementation.py` so it satisfies the ordinary and refusal cases in `tests/unit/test_applied_file.py`. Consider the task, then the status, then the project, then whether the project folder exists, then the account, then the class, then the file name, then whether the file stays inside the project, then whether the destination folder exists. Resolve a relative project path from the startup folder captured in T002. Use an absolute project path as given. Store the trimmed project path the engineer typed. For `ordinary` with no stop and a missing file, create that file exclusively with the submitted UTF-8 text and insert an `implementation_change` of class `ordinary`, an `assistant_change` row with `stopped` `0`, and an `applied_file` row with `was_new` `1`, `previous_text` absent, and `file_text` equal to the submitted text, which may be empty. Copy `assistant_name` from `workspace_assistant`, never from the caller. Keep `implementation_change.engineer_name` as the workspace engineer. Return the task detail. Do not create the project folder or a missing folder inside it. Do not follow a link outside the resolved project folder. Do not verify a criterion, record a check, record a decision, or change task status. Leave `record` unchanged.
- [X] T008 [US1] Extend `record_assistant_change` in `src/task_manager/workspace.py` so it accepts the file path and the file text and runs T007 inside the existing transaction and clock, passing the startup folder from T002. Omitting the file path must stay possible for feature 005; do not require it in this task's signature default.
- [X] T009 [US1] Extend `POST /api/tasks/{id}/assistant-changes` in `src/task_manager/web/api.py` with optional `file` and `file_text`, per `specs/006-apply-ordinary-file/contracts/http-api.md`. Omitting `file` keeps the feature 005 command. A blank `file` is the file-name refusal. Omitting `file_text` while sending `file` means empty text. Ignore `file_text` when `file` is omitted. Ignore extra fields, including `assistant_name` and `engineer_name`. Return the task detail or the refusal from that contract.
- [X] T010 [US1] Add the file path and the file text to the assistant form on `src/task_manager/web/templates/detail.html`, and show `file.path`, whether the file was new, `file.previous_text` when present, and `file.text` on a change that has a file. Accept the form in `src/task_manager/web/pages.py` at `POST /tasks/{task_id}/assistant-changes`. Show the form only when the task is In Progress. A refusal redisplays the detail with the API message and the same stored task. A success redisplays the detail without changing the status. A Cancelled task shows stored file fields and does not offer the form.

**Checkpoint**: User Story 1 is functional on its own — write one new ordinary file and read the path, the text, the assistant, and Carried out on that task

---

## Phase 4: User Story 2 - Wait before changing a file that is already there (Priority: P2)

**Goal**: A replacement, a consequential request, and a stopped request do not change the project. The task shows class consequential and Awaiting approval. The engineer approves or declines later. Approval writes the file only when it still matches. The assistant cannot approve or decline.

**Independent Test**: On one In Progress task, ask the assistant to replace an existing file, or to stop an ordinary new file. The file on disk is unchanged and the task shows Awaiting approval until the engineer approves or declines.

### Tests for User Story 2 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T011 [P] [US2] Add failing unit tests in `tests/unit/test_applied_file_approval.py` for: an ordinary request that names an existing text file stores `class` `consequential`, `stopped` false, `file.was_new` false, `file.previous_text` equal to the current text, and `file.text` equal to the proposed text, and does not change the file; a consequential request for a new file stores `class` `consequential`, `stopped` false, `file.was_new` true, and does not create the file; an ordinary request with the stop set stores `class` `consequential`, `stopped` true, and does not create the file; an existing file that cannot be decoded as UTF-8, contains a NUL byte, or is a folder is refused with `The file is not text.` and writes no row and does not change the file; an approve call whose actor is `assistant` is refused with `The assistant cannot approve a change.` before any file read or write; a decline call whose actor is `assistant` is refused with `The assistant cannot decline a change.` and leaves the change Awaiting approval; the engineer can approve a waiting new file that is still absent, the file is created with the proposed text, the approval `engineer_name` is `Ada`, and the outcome becomes Carried out; the engineer can approve a replacement only while the file still contains `previous_text`, and the file then contains the proposed text; when the file text changed, the file appeared, the file is no longer text, or the resolved path now lands outside the project, approval writes no resolution and does not change the file, using `The file no longer matches the text this change was proposed against.` or `The file must stay inside the named project.` as specified in `specs/006-apply-ordinary-file/contracts/http-api.md`; the engineer can mark a waiting file not carried out with a reason and the file stays unchanged; approving an ordinary file that is already Carried out is refused with `An ordinary change does not wait for approval.` and does not write the file again.
- [X] T012 [P] [US2] Add failing contract tests in `tests/contract/test_applied_file_approval_api.py` for `POST /api/tasks/{id}/assistant-changes` with an existing file, with `class` `consequential`, and with `class` `ordinary` plus `stopped` true, and for approve and decline with `actor` `assistant`. Assert the status codes and exact messages in `specs/006-apply-ordinary-file/contracts/http-api.md`. Assert a successful engineer approval names `Ada` in `approval.engineer_name` and writes the proposed text. Assert a mismatch leaves the file unchanged.

### Implementation for User Story 2

- [X] T013 [US2] Extend the assistant-file command and `approve` in `src/task_manager/domain/implementation.py` so they satisfy `tests/unit/test_applied_file_approval.py`. Store a consequential request, a stopped ordinary request, and an ordinary request whose file already exists as class `consequential`, and do not change the project. Set `stopped` to `1` only when the request class was ordinary and the request was stopped; a replacement that was not stopped stores `stopped` `0`. Set `was_new` to `0` and store `previous_text` when the file existed. If exclusive create finds the new file already there, store the replacement row instead and do not overwrite it. On approve, refuse actor `assistant` before any file read or write. Write the proposed text only when the change is still Awaiting approval, the resolved file still lands inside the resolved project, a new file is still absent, and an existing file still contains `previous_text` and is still text. Create a new file exclusively. Replace an existing file's text only after that match. Write the approval row in the same command as a successful write. A failed check writes no resolution and does not change the file. Decline does not write. An omitted actor stays the engineer's existing approve and decline path.

**Checkpoint**: User Stories 1 and 2 work — a new ordinary file is written, and a replacement, a consequential request, or a stopped request waits for the engineer

---

## Phase 5: User Story 3 - Read the written file without asking again (Priority: P3)

**Goal**: The stored file record is what a later reader uses. An assistant change with no file, and the engineer's own change, write nothing. A subtask file stays on the subtask. The assistant does not check, decide, or complete the task.

**Independent Test**: Write one ordinary new file, read the task, and confirm a second read shows the same file, text, assistant, and outcome without modifying the file again.

### Tests for User Story 3 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T014 [P] [US3] Add failing unit tests in `tests/unit/test_applied_file_record.py` for: an assistant change with no file path stores no `applied_file` row, reports `file` null, and does not create a file for the named project; `record` with a `project`, an `assistant_name`, and a file path still stores an engineer change whose `file` is null and does not write that file; an applied file on a subtask appears on the subtask and does not appear on the parent; recording an applied file does not insert a check or a decision; completing an otherwise legal task that has a carried-out file change with no passing check stays In Progress and includes `Needs a passing check:`; reading the stored task does not change the file bytes; there is no domain function that updates or deletes an `applied_file` row or calls a model.
- [X] T015 [P] [US3] Add failing contract tests in `tests/contract/test_applied_file_record_api.py` for `POST /api/tasks/{id}/assistant-changes` with no `file` field and for `POST /api/tasks/{id}/implementation-changes` with extra `project`, `file`, and `file_text` fields. Assert the assistant command without `file` keeps `recorded_by` `assistant` and `file` null, and writes no project file. Assert the engineer command ignores those extra fields, stores `recorded_by` `engineer` and `file` null, and writes no project file. Assert `GET /api/tasks/{id}` for a parent does not list a subtask's applied file.

### Implementation for User Story 3

- [X] T016 [US3] Keep a missing `file` on `POST /api/tasks/{id}/assistant-changes` in `src/task_manager/web/api.py`, and `record` in `src/task_manager/domain/implementation.py`, from writing `applied_file` or any project file. Keep `POST /api/tasks/{id}/implementation-changes` from writing a file when `project`, `file`, or `file_text` is sent. Keep change lists in `src/task_manager/storage/implementation_store.py` filtered by that task's id so a subtask file is not copied onto the parent. Do not add a model call, a folder creator, or a completion guard in `src/task_manager/domain/status.py`; the feature 003 guard already covers a carried-out file change.

**Checkpoint**: All three stories work — the stored file is the record, a change with no file writes nothing, and completion still waits for a passing check

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Replay and the quickstart

- [X] T017 Extend `tests/integration/test_replay.py` so the same script — record one ordinary new file with project `billing`, file `notes/label.txt`, account `Rename the export label`, and text `Export` — run twice, each time with a fresh project folder and the same `ScriptedClock`, produces the same file path, text, assistant name, Carried out outcome, and order, writes each folder once, and does not call a model
- [X] T018 Run the three manual scenarios in `specs/006-apply-ordinary-file/quickstart.md` against a fresh `workspace.db` and a fresh `billing` folder, and fix any mismatch in `src/task_manager/` before treating the feature as done

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **User Stories (Phase 3–5)**: Depend on Foundational
- **Polish (Phase 6)**: Depends on the user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Foundational. No dependency on other stories
- **User Story 2 (P2)**: Starts after User Story 1, because it extends the same file command with replacement, stop, and approval
- **User Story 3 (P3)**: Starts after User Story 1, because it reads a file that story records. It does not depend on User Story 2. The omitted-file and engineer-command rules are tested on their own in `tests/unit/test_applied_file_record.py`

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Domain rules before the workspace method
- Workspace method before the HTTP route and the page
- Story checkpoint before the next story

### Parallel Opportunities

- T005 and T006 can run in parallel
- T011 and T012 can run in parallel
- T014 and T015 can run in parallel
- T003 and T004 stay sequential because both edit `src/task_manager/storage/implementation_store.py`
- Story phases that share `src/task_manager/domain/implementation.py`, `src/task_manager/web/api.py`, and `src/task_manager/web/templates/detail.html` stay sequential for those files
- T017 starts after those stories, because the replay script records a file

---

## Parallel Example: User Story 1

```bash
# Write the failing User Story 1 tests together:
Task: "T005 tests/unit/test_applied_file.py"
Task: "T006 tests/contract/test_applied_file_api.py"

# Then implement in order: T007 domain, T008 workspace, T009 API, T010 pages
```

## Parallel Example: User Story 2

```bash
Task: "T011 tests/unit/test_applied_file_approval.py"
Task: "T012 tests/contract/test_applied_file_approval_api.py"
```

## Parallel Example: User Story 3

```bash
Task: "T014 tests/unit/test_applied_file_record.py"
Task: "T015 tests/contract/test_applied_file_record_api.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Run `tests/unit/test_applied_file.py` and `tests/contract/test_applied_file_api.py`
5. Demo one new ordinary file before adding replacement and approval

### Incremental Delivery

1. Setup + Foundational → the file row and the `file` field on each change
2. User Story 1 → write one new ordinary file (MVP)
3. User Story 2 → a replacement, a consequential request, and a stopped request wait for the engineer
4. User Story 3 → keep a change with no file, and the engineer's command, from writing a project
5. Polish → replay test and quickstart scenarios

### Parallel Team Strategy

With multiple people:

1. Complete Setup and Foundational together
2. After that, one person owns User Story 1 through its checkpoint
3. User Story 2 then owns replacement, stop, and approval in `src/task_manager/domain/implementation.py`
4. User Story 3 owns the proof that a missing file and `record` write nothing
5. Within a story, the failing tests can be written at the same time

---

## Notes

- [P] tasks = different files, no dependencies on incomplete work
- [US1]–[US3] map to the three stories in spec.md
- Verify each story's tests fail before implementing that story
- Do not call a model, create a missing folder, or write outside the resolved project folder
- Do not infer ordinary or consequential from the file text, except that an existing file is stored as consequential
- Ordinary still means the file was written
- Do not let the assistant approve or decline a change
- Do not refuse completion with a new sentence; a carried-out file change already needs a passing check
- Commit after each task or logical group
- Stop at any checkpoint to validate that story alone
