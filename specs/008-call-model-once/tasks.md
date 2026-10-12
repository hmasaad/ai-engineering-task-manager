---
description: "Task list for Call the Model Once"
---

# Tasks: Call the Model Once

**Input**: Design documents from `/specs/008-call-model-once/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Included. Constitution Principle II requires a failing test before each behavior. The tests were written and failed on the missing command, then the command was implemented.

**Organization**: Tasks are grouped by user story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)

## Phase 1: Setup

- [X] T001 Add `model_call` to `src/task_manager/storage/schema.sql`. `change_id` is the primary key and references `implementation_change(id)`. `file_read_id` is required and references `file_read(id)`. `model_name` is required and non-empty. `model_input` is required and non-empty. `model_output` is required and may be empty. No update or delete.

## Phase 2: Foundational

- [X] T002 Add `ScriptedModel` in `src/task_manager/model.py` with a name, a fixed text, and a list of prompts passed to `complete`.
- [X] T003 Add insert and file-read lookup in `src/task_manager/storage/model_store.py`. Do not update or delete a model call.
- [X] T004 Add `model` to each change from `change_payload` in `src/task_manager/storage/implementation_store.py`. It is null when no `model_call` row exists. Otherwise it has `name`, `input`, `output`, and `file_read_id`.

## Phase 3: User Story 1 - Ask the model for one new file (Priority: P1)

- [X] T005 [P] [US1] Add failing unit tests in `tests/unit/test_model_file.py` for one ordinary new file, refusals that do not call the model, a missing model, and a failed call.
- [X] T006 [P] [US1] Add failing contract tests in `tests/contract/test_model_file_api.py` for `POST /api/tasks/{id}/model-files` using the status codes and messages in `specs/008-call-model-once/contracts/http-api.md`.
- [X] T007 [US1] Implement `record_model_file` in `src/task_manager/domain/model_file.py`. Call the configured model once only after the task, project, account, class, file, file read, and placement checks pass. Store the prompt and the returned text. Write a new ordinary file through the existing assistant-file command.
- [X] T008 [US1] Add `record_model_file` on `Workspace` in `src/task_manager/workspace.py`, `POST /api/tasks/{id}/model-files` in `src/task_manager/web/api.py`, and the model form and model line in `src/task_manager/web/pages.py` and `src/task_manager/web/templates/detail.html`.

## Phase 4: User Story 2 - Wait before replacing a file (Priority: P2)

- [X] T009 [US2] Cover replacement and approval in `tests/unit/test_model_file.py`. Approval writes the stored model text and does not call the model again. The assistant cannot approve.

## Phase 5: User Story 3 - Replay the stored model text (Priority: P3)

- [X] T010 [US3] Extend `tests/integration/test_replay.py` so the same script calls the model once per fresh project folder, the stored model name and output match, and opening the task does not call the model again. An assistant change that submits its own file text stores no model call.

## Phase 6: Polish

- [X] T011 Pass `--model-name` and `--model-text` through `src/task_manager/__main__.py` to a `ScriptedModel`.
- [X] T012 Run the manual scenarios in `specs/008-call-model-once/quickstart.md` against a fresh workspace and a fresh `billing` folder.

## Dependencies

- Setup and foundational work come before the stories.
- User Story 1 is the MVP. User Story 2 uses the same command. User Story 3 replays a stored call.
- Tests for a story are written before that story's command is considered done.
