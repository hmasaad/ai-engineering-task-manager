---
description: "Task list for Instruction Page"
---

# Tasks: Instruction Page

**Input**: Design documents from `/specs/023-instruction-page/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Included. The spec says the rules are covered by automated checks. Constitution Principle II requires a failing test before the behavior exists.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested on its own.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Single project: `src/task_manager/`, `tests/` at the repository root

## Phase 1: Setup

**Purpose**: The saved-model table. `task` gains no column.

- [X] T001 Add `configured_model` in `src/task_manager/storage/schema.sql` with `CREATE TABLE IF NOT EXISTS` only, `id` fixed at 1, `model_name` trimmed and not empty, and `model_text` not empty after trimming, as in `specs/023-instruction-page/data-model.md`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The workspace can read and replace the saved model before the page exists.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T002 Add read and replace of the single `configured_model` row in `src/task_manager/storage/model_config_store.py`. Load it from `src/task_manager/workspace.py` when the process was not given a model.

**Checkpoint**: A saved model can be read. Starting work does not exist yet.

---

## Phase 3: User Story 1 - Set the model on the page (Priority: P1) 🎯 MVP

**Goal**: Saving a model name and text keeps them for the next opening.

**Independent Test**: Save "Guide" and "Export". Open the same workspace file. The model is still "Guide" and "Export".

### Tests for User Story 1

- [X] T003 [P] [US1] Write the save, reopen, and blank-field checks in `tests/unit/test_instruction_page.py`. Confirm they fail before the behavior exists.

### Implementation for User Story 1

- [X] T004 [US1] Save and return the model from `src/task_manager/domain/instruction.py` and `src/task_manager/workspace.py`. A blank name uses `Choose the model this change uses.` A blank text uses `Name the text the model returns.`

**Checkpoint**: The saved model survives opening the workspace again.

---

## Phase 4: User Story 2 - Start work from one instruction (Priority: P2)

**Goal**: One request creates the task, reads one file, and asks the model once.

**Independent Test**: Start work for a new ordinary file. The task is In Progress, the file contains the model text, and one file read is stored. A missing file stores no task.

### Tests for User Story 2

- [X] T005 [P] [US2] Extend `tests/unit/test_instruction_page.py` for a new file, a waiting replacement, and a refusal that stores nothing.
- [X] T006 [P] [US2] Add `tests/contract/test_instruction_page_api.py` for `POST /api/model`, `POST /api/instructions`, and `GET /api/tasks` remaining a list.

### Implementation for User Story 2

- [X] T007 [US2] In `src/task_manager/domain/instruction.py`, start work in one transaction through the existing task, read, and model proposal. Expose it from `src/task_manager/workspace.py` and `src/task_manager/web/api.py`.

**Checkpoint**: A refused start leaves no task and no file.

---

## Phase 5: User Story 3 - Find the page from the task list (Priority: P3)

**Goal**: Instructions is linked from the task list and starts work in the browser.

**Independent Test**: The task list links to Instructions. The page shows the model fields and the task fields. A successful start opens the task.

### Tests for User Story 3

- [X] T008 [P] [US3] In `tests/contract/test_instruction_page_api.py`, assert the task list links to Instructions and the page contains the field ids from `specs/023-instruction-page/contracts/commands.md`.

### Implementation for User Story 3

- [X] T009 [US3] Add `src/task_manager/web/templates/instructions.html`, the routes in `src/task_manager/web/pages.py`, and the Instructions link in `src/task_manager/web/templates/base.html`.

**Checkpoint**: The engineer can save the model and start work from the page.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T010 Run the checks in `specs/023-instruction-page/quickstart.md` and confirm the existing suite stays green.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on T001. Blocks the stories.
- **User Story 1 (Phase 3)**: Depends on Phase 2.
- **User Story 2 (Phase 4)**: Depends on User Story 1, because start work uses the saved model.
- **User Story 3 (Phase 5)**: Depends on User Story 2, because the page posts that command.
- **Polish (Phase 6)**: Depends on the stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Independently testable by saving and opening the workspace.
- **User Story 2 (P2)**: Independently testable once a model is saved.
- **User Story 3 (P3)**: Depends on the commands the page posts.

### Parallel Opportunities

- T005 and T006 touch different test files and can be written together.

### Parallel Example: User Story 2

```bash
tests/unit/test_instruction_page.py
tests/contract/test_instruction_page_api.py
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete User Story 1.
3. Stop and validate the saved model.

### Incremental Delivery

1. Save the model.
2. Start one file change from the instruction.
3. Link the page from the task list.

## Notes

- A failed start rolls back. Do not leave a Draft task behind.
- Do not add a column to `task`.
- Commit only when the engineer asks.
