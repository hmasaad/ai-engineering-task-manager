---
description: "Task list for Real Model"
---

# Tasks: Real Model

**Input**: Design documents from `/specs/024-real-model/`

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

**Purpose**: The model service table. `configured_model` is not altered and is not read.

- [X] T001 Add `model_service` in `src/task_manager/storage/schema.sql` with `CREATE TABLE IF NOT EXISTS` only, `id` fixed at 1, `model_name` trimmed and not empty, `base_url` trimmed and not empty, and `api_key` null or not empty after trimming, as in `specs/024-real-model/data-model.md`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The workspace can load a service instead of fixed model text.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T002 Read and replace the single `model_service` row in `src/task_manager/storage/model_config_store.py`. Load it from `src/task_manager/workspace.py` when the process was not given a model. Do not read `configured_model`.

**Checkpoint**: A saved service can be loaded. Starting work does not call it yet.

---

## Phase 3: User Story 1 - Name the model service (Priority: P1) 🎯 MVP

**Goal**: Saving a name, address, and optional key keeps them for the next opening.

**Independent Test**: Save "Guide" and an address. Open the same workspace file. The name and address remain. A blank address is refused.

### Tests for User Story 1

- [X] T003 [P] [US1] Rewrite the save checks in `tests/unit/test_instruction_page.py` for a service address and an optional key. Confirm they fail before the behavior exists.

### Implementation for User Story 1

- [X] T004 [US1] Save the service from `src/task_manager/domain/instruction.py`. A blank name uses `Choose the model this change uses.` A blank or non-http address uses `Name the model service.`

**Checkpoint**: The saved service survives opening the workspace again.

---

## Phase 4: User Story 2 - The model revises one file (Priority: P2)

**Goal**: One start asks the service once and uses the reply as the file text.

**Independent Test**: An existing file stays unchanged while the reply waits for approval. An unreachable service stores no task.

### Tests for User Story 2

- [X] T005 [P] [US2] Extend `tests/unit/test_instruction_page.py` with a local service that returns a revised file, an unreachable address, and an empty reply.
- [X] T006 [P] [US2] Update `tests/contract/test_instruction_page_api.py` for `POST /api/model` without model text and `POST /api/instructions` against a local service.

### Implementation for User Story 2

- [X] T007 [US2] Add the service call in `src/task_manager/model.py`. Include what changed and the file text in the prompt in `src/task_manager/domain/model_file.py`. An unreachable service uses `The model service could not be reached.` An empty reply uses `The model did not return file text.`

**Checkpoint**: A refused start leaves no task and no file.

---

## Phase 5: User Story 3 - The page no longer asks for model text (Priority: P3)

**Goal**: Instructions shows Model address and API key, and not Model text.

**Independent Test**: The task list links to Instructions. The page has `model-address` and `model-key` and no `model-text`.

### Tests for User Story 3

- [X] T008 [P] [US3] In `tests/contract/test_instruction_page_api.py`, assert the page fields from `specs/024-real-model/contracts/commands.md`.

### Implementation for User Story 3

- [X] T009 [US3] Replace the model text field in `src/task_manager/web/templates/instructions.html`, `src/task_manager/web/pages.py`, and `src/task_manager/web/api.py`.

**Checkpoint**: The engineer saves a service and sees the reply on the task.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T010 Run the checks in `specs/024-real-model/quickstart.md` and confirm the existing suite stays green.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on T001. Blocks the stories.
- **User Story 1 (Phase 3)**: Depends on Phase 2.
- **User Story 2 (Phase 4)**: Depends on User Story 1, because the start uses the saved service.
- **User Story 3 (Phase 5)**: Depends on User Story 2, because the page posts that service.
- **Polish (Phase 6)**: Depends on the stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Independently testable by saving and opening the workspace.
- **User Story 2 (P2)**: Independently testable once a service is saved.
- **User Story 3 (P3)**: Depends on the fields the service command accepts.

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
3. Stop and validate the saved service.

### Incremental Delivery

1. Save the service.
2. Ask it once for the revised file.
3. Remove model text from the page.

## Notes

- A failed start rolls back. Do not leave a task behind.
- Do not put the key in the stored prompt.
- Commit only when the engineer asks.
