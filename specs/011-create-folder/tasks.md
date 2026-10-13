# Tasks: Create One Folder

**Input**: `specs/011-create-folder/spec.md`

## Phase 1

- [X] T001 Add `created_folder` to `src/task_manager/storage/schema.sql`. `change_id` is the primary key and references `implementation_change(id)`. `folder_path` is required and non-empty after trimming.
- [X] T002 Record one folder from `src/task_manager/domain/folder.py`, show it on the task, and create it on an ordinary request. A consequential or stopped request waits. Approval creates the folder. The assistant cannot approve.
- [X] T003 Cover the command in `tests/unit/test_folder.py` and `tests/contract/test_folder_api.py`.

## Notes

- A file write still requires the destination folder to exist.
- Running a test, deleting a file, committing, and opening a pull request are separate later features.
