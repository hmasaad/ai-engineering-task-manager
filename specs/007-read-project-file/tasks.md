---
description: "Task list for Read a Project File"
---

# Tasks: Read a Project File

**Input**: Design documents from `/specs/007-read-project-file/`

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
- A test that reads a project file passes a temporary directory as the workspace startup folder. The suite must not read or write a project file inside the repository.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add the stored table this feature needs. The Python package, clock, assistant name, startup folder, and process shell already exist.

- [X] T001 Add `file_read` to `src/task_manager/storage/schema.sql` with `CREATE TABLE IF NOT EXISTS`, so an existing workspace file gains it when `src/task_manager/storage/connection.py` runs the script. `id` is the primary key and is assigned at insert. `task_id` is required and references `task(id)`. `project` is required and non-empty after trimming. `file_path` is required and non-empty after trimming. `file_text` is required and may be empty. `assistant_name` is required and non-empty after trimming. `read_at` is required. No update or delete statement for `file_read`. Do not add a column to `implementation_change`, `assistant_change`, or `applied_file`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Store and return one read row. Every story reads the task through the existing task detail.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T002 Implement insert and list functions in `src/task_manager/storage/file_read_store.py` for `file_read`. Insert one row with `task_id`, trimmed `project`, trimmed `file_path`, `file_text` which may be empty and is not trimmed, `assistant_name`, and `read_at`. List rows for one task id oldest first, by `read_at` then `id`. Do not check task status or the filesystem. Do not add a function that updates or deletes `file_read`.
- [X] T003 Add `file_reads` to the task detail returned by `task_detail` in `src/task_manager/storage/task_store.py`, using T002. The list contains only rows for that task id, oldest first. Each object has `id`, `project`, `path` from `file_path`, `text` from `file_text`, `assistant_name`, and `read_at`. A task with no rows has an empty list. Leave feature 001 through feature 006 fields unchanged. A subtask row is not copied onto the parent.

**Checkpoint**: Foundation ready — user story implementation can now begin

---

## Phase 3: User Story 1 - Read one text file (Priority: P1) 🎯 MVP

**Goal**: An engineer asks for one existing text file to be read for an In Progress task in an existing project folder. The task shows the path, the text, the project path, the assistant, and the time. The file is unchanged. The task stays In Progress. No implementation change is required for this story's page yet beyond showing the read.

**Independent Test**: On one In Progress task, name an existing project folder and one text file inside it. The task shows that file's text, its path, the project, and the assistant, and the file in the project is unchanged.

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T004 [P] [US1] Add failing unit tests in `tests/unit/test_file_read.py` that pass a temporary startup folder into `Workspace` and call the file-read command. Assert: a blank or whitespace project is refused with `Name the project this change is for.` and writes no row and does not change a file; a project path that is missing or is not a folder is refused with `The project must already exist.` and writes nothing; when the project and the file name are both blank, the refusal is `Name the project this change is for.`; a blank or whitespace file name is refused with `Name the file this change reads.` and writes nothing; an absolute file path or a file path that climbs out of the project, including a link that lands outside, is refused with `The file must stay inside the named project.` and stores nothing outside the project; a missing file, including a missing folder inside the project, is refused with `The file must already exist.` and does not create that folder; a file that cannot be decoded as UTF-8, contains a NUL byte, or is a folder is refused with `The file is not text.` and does not change the file; a read of `notes/label.txt` containing `Export` in an existing project folder `billing` stores `project` `billing` as typed, `path` `notes/label.txt`, `text` `Export`, and `assistant_name` `Guide` rather than a name from the caller, leaves the file bytes unchanged, adds no implementation change, and leaves the task In Progress; a link that stays inside the project stores the path the engineer named and the text the link reaches; an empty file stores an empty `text` and stays empty; a file whose text is `Export ` stores `Export ` including the trailing space; task status, criterion Verified state, checks, decisions, and status history stay unchanged; Draft is refused with `The task must be In Progress.`; Ready is refused with `Start the task first.`; Completed is refused with `Reopen the task first.`; Cancelled is refused with `A cancelled task cannot be changed. Continued work is a new task.`; a wrong status is refused before a blank project or a blank file name; an unknown task id is refused with `Task not found.`
- [X] T005 [P] [US1] Add failing contract tests in `tests/contract/test_file_read_api.py` for `POST /api/tasks/{id}/file-reads` and `GET /api/tasks/{id}` using the status codes and exact messages in `specs/007-read-project-file/contracts/http-api.md`. Use a temporary startup folder that already contains `billing/notes/label.txt` with text `Export`. Assert the new read is last in `file_reads`, `text` is `Export`, `assistant_name` is `Guide`, and body fields `assistant_name` and `engineer_name` are ignored. Assert a refused command returns `{"refused": true, "message": "..."}` and leaves the task status and the project file unchanged. Assert a wrong-shaped body, including a missing `project` or `file`, is 400 with `The request is missing a required field or has the wrong shape.`

### Implementation for User Story 1

- [X] T006 [US1] Implement the read command in `src/task_manager/domain/file_read.py` so it satisfies the success and refusal cases in `tests/unit/test_file_read.py`. Consider the task, then the status, then the project, then whether the project folder exists, then the file name, then whether the file stays inside the project, then whether the file exists, then whether it is text. Reuse the inside-project and text checks already used by `src/task_manager/domain/implementation.py`. Resolve a relative project path from the startup folder already captured on `Workspace`. Use an absolute project path as given. Store the trimmed project path the engineer typed and the relative file path. Read the file as UTF-8 without a NUL byte and insert one `file_read` row whose `file_text` is that text, including spaces and including an empty string. Copy `assistant_name` from `workspace_assistant`, never from the caller. Return the task detail. Do not create the project folder or a missing folder inside it. Do not write, replace, or delete the file. Do not follow a link outside the resolved project folder. Do not insert an implementation change, an assistant change, or an applied file. Do not verify a criterion, record a check, record a decision, or change task status.
- [X] T007 [US1] Add `record_file_read` in `src/task_manager/workspace.py` so it accepts the project path and the file path and runs T006 inside the existing transaction and clock, passing the startup folder. Do not change `record` or `record_assistant_change`.
- [X] T008 [US1] Add `POST /api/tasks/{id}/file-reads` in `src/task_manager/web/api.py` per `specs/007-read-project-file/contracts/http-api.md`. Require `project` and `file` as strings. Ignore extra fields, including `assistant_name` and `engineer_name`. Return the task detail or the refusal from that contract. Do not change `POST /api/tasks/{id}/assistant-changes`.
- [X] T009 [US1] Add a read form, with a project and a file path and no file text, to `src/task_manager/web/templates/detail.html`, and show each read's path, text, project, assistant, and time, oldest first, separate from implementation changes. Accept the form in `src/task_manager/web/pages.py` at `POST /tasks/{task_id}/file-reads`. Show the form only when the task is In Progress. A refusal redisplays the detail with the API message and the same stored task. A success redisplays the detail without changing the status. A task with no reads shows no read lines.

**Checkpoint**: User Story 1 is functional on its own — read one existing text file and see the path, the text, the project, and the assistant on that task

---

## Phase 4: User Story 2 - Read the stored text again (Priority: P2)

**Goal**: Opening the task shows the stored text. Replay and a later edit or deletion of the file do not change that row and do not read the file again. A second read stores the later text as a new row. A subtask read stays on the subtask.

**Independent Test**: Read one text file, change that file, then open the task. The task still shows the original text, and opening it does not read the file again.

### Tests for User Story 2 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T010 [P] [US2] Add failing unit tests in `tests/unit/test_file_read_record.py` for: after a stored read of `Export`, changing the file to `Newer` or deleting it leaves the stored `text` as `Export` and `get_task` does not change the file bytes; a second read after the file contains `Newer` appends a second row and leaves the first row as `Export`, oldest first; a read on a subtask appears on the subtask and does not appear on the parent; there is no domain or storage function that updates or deletes a `file_read` row or calls a model.
- [X] T011 [P] [US2] Add failing contract tests in `tests/contract/test_file_read_record_api.py` for `GET /api/tasks/{id}` after the project file has changed, and for a second `POST /api/tasks/{id}/file-reads` of the same path. Assert the first `file_reads` entry still has the original `text` and the second entry has the later text. Assert `GET /api/tasks/{id}` for a parent does not list a subtask's read.

### Implementation for User Story 2

- [X] T012 [US2] Keep `task_detail` in `src/task_manager/storage/task_store.py` and the list function in `src/task_manager/storage/file_read_store.py` returning stored rows only, ordered by `read_at` then `id`, without opening the project folder. A second successful call of the read command in `src/task_manager/domain/file_read.py` inserts another row and does not modify the earlier row. Do not add an update or delete function.

**Checkpoint**: User Stories 1 and 2 work — the stored text stays put when the file changes, and a later read is a second row

---

## Phase 5: User Story 3 - Leave the project and the other records alone (Priority: P3)

**Goal**: A read is not an implementation change. Earlier assistant changes and the engineer's own change do not read a project file. Completion still waits for a passing check of a carried-out change. The assistant does not check, decide, or complete the task.

**Independent Test**: Read one file on a task that also has a carried-out file change. The read is shown separately, the project file is unchanged, and completing the task still waits for a passing check of that carried-out change.

### Tests for User Story 3 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T013 [P] [US3] Add failing unit tests in `tests/unit/test_file_read_isolation.py` for: a successful read adds no implementation change and does not show a class, Carried out, or Awaiting approval for that read; a waiting file proposal stays Awaiting approval when that file is read, and the file bytes stay unchanged; an assistant change with no file path stores no `file_read` row and does not create a file; `record` with a `project` and a file path stores no `file_read` row and does not read that file into the task; recording a read does not insert a check or a decision; completing an otherwise legal task that has a carried-out file change with no passing check stays In Progress and includes `Needs a passing check:`; cancelling the task leaves the stored read visible.
- [X] T014 [P] [US3] Add failing contract tests in `tests/contract/test_file_read_isolation_api.py` for `POST /api/tasks/{id}/assistant-changes` with no `file` field and for `POST /api/tasks/{id}/implementation-changes` with extra `project` and `file` fields. Assert neither command adds a `file_reads` entry or changes a project file. Assert a successful `POST /api/tasks/{id}/file-reads` leaves `implementation_changes` unchanged.

### Implementation for User Story 3

- [X] T015 [US3] Keep `record` in `src/task_manager/domain/implementation.py`, `POST /api/tasks/{id}/assistant-changes`, and `POST /api/tasks/{id}/implementation-changes` in `src/task_manager/web/api.py` from inserting `file_read` or reading a project file into the task. Keep a missing `file` on the assistant-change command from opening the project. Do not add a model call or a completion guard in `src/task_manager/domain/status.py`. On `src/task_manager/web/templates/detail.html`, a Cancelled task shows stored reads and does not offer the read form.

**Checkpoint**: All three stories work — a read is stored on its own, older commands do not read a file, and completion still waits for a passing check

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Replay and the quickstart

- [X] T016 Extend `tests/integration/test_replay.py` so the same script — read one existing file with project `billing` and file `notes/label.txt` whose text is `Export` — run twice, each time with a fresh project folder containing that same file text and the same `ScriptedClock`, produces the same path, text, project, assistant name, and order, reads each folder once, and does not call a model. Opening the stored task must not read the file again.
- [X] T017 Run the three manual scenarios in `specs/007-read-project-file/quickstart.md` against a fresh `workspace.db` and a fresh `billing` folder, and fix any mismatch in `src/task_manager/` before treating the feature as done

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **User Stories (Phase 3–5)**: Depend on Foundational
- **Polish (Phase 6)**: Depends on the user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Foundational. No dependency on other stories
- **User Story 2 (P2)**: Starts after User Story 1, because it reads a row that story stores
- **User Story 3 (P3)**: Starts after User Story 1, because it proves that read is not an implementation change. It does not depend on User Story 2

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Storage before the domain command
- Domain command before the workspace method
- Workspace method before the HTTP route and the page
- Story checkpoint before the next story

### Parallel Opportunities

- T004 and T005 can run in parallel
- T010 and T011 can run in parallel
- T013 and T014 can run in parallel
- T002 and T003 stay sequential because T003 reads through T002
- Story phases that share `src/task_manager/domain/file_read.py`, `src/task_manager/web/api.py`, and `src/task_manager/web/templates/detail.html` stay sequential for those files
- T016 starts after those stories, because the replay script records a read

---

## Parallel Example: User Story 1

```bash
# Write the failing User Story 1 tests together:
Task: "T004 tests/unit/test_file_read.py"
Task: "T005 tests/contract/test_file_read_api.py"

# Then implement in order: T006 domain, T007 workspace, T008 API, T009 pages
```

## Parallel Example: User Story 2

```bash
Task: "T010 tests/unit/test_file_read_record.py"
Task: "T011 tests/contract/test_file_read_record_api.py"
```

## Parallel Example: User Story 3

```bash
Task: "T013 tests/unit/test_file_read_isolation.py"
Task: "T014 tests/contract/test_file_read_isolation_api.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Run `tests/unit/test_file_read.py` and `tests/contract/test_file_read_api.py`
5. Demo one stored read before adding the later-edit and isolation stories

### Incremental Delivery

1. Setup + Foundational → the read row and the `file_reads` field on the task
2. User Story 1 → read one existing text file (MVP)
3. User Story 2 → the stored text stays when the file changes
4. User Story 3 → keep older commands from reading a project file
5. Polish → replay test and quickstart scenarios

### Parallel Team Strategy

With multiple people:

1. Complete Setup and Foundational together
2. After that, one person owns User Story 1 through its checkpoint
3. User Story 2 then owns the proof that a stored row is not read again
4. User Story 3 owns the proof that older commands store no read
5. Within a story, the failing tests can be written at the same time

---

## Notes

- [P] tasks = different files, no dependencies on incomplete work
- [US1]–[US3] map to the three stories in spec.md
- Verify each story's tests fail before implementing that story
- Do not call a model, create a missing folder, or write a project file
- Do not store a read as an implementation change
- Do not let a client-supplied assistant name replace the configured assistant
- Do not refuse completion with a new sentence; a carried-out file change already needs a passing check
- Commit after each task or logical group
- Stop at any checkpoint to validate that story alone
