# Tasks: Delete One File

**Input**: `specs/013-delete-file/spec.md`

## Phase 1

- [X] T001 Add `deleted_file` to `src/task_manager/storage/schema.sql`. `change_id` is the primary key and references `implementation_change(id)`. `file_path` is required. `previous_text` is required and may be empty.
- [X] T002 Record one delete from `src/task_manager/domain/delete_file.py`. Every request waits. Store the path and the text the file had. Approval removes the file only when that text is unchanged. The assistant cannot approve. Decline and opening the task do not remove the file.
- [X] T003 Cover the command in `tests/unit/test_delete_file.py` and `tests/contract/test_delete_api.py`.

## Notes

- A file write, a folder, and a test run keep their current rules.
- Committing and opening a pull request are separate later features.
