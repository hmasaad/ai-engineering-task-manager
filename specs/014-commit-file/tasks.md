# Tasks: Commit One File

**Input**: `specs/014-commit-file/spec.md`

## Phase 1

- [X] T001 Add `committed_file` and `committed_revision` to `src/task_manager/storage/schema.sql`. `committed_file.change_id` references `implementation_change(id)` and stores the path and text. `committed_revision` is inserted only after the commit succeeds and stores the commit hash.
- [X] T002 Commit one named file from `src/task_manager/domain/commit_file.py`. Every request waits. Approval runs `git commit -m` for that path only, with no `--no-verify`, no `--amend`, no config change, and no other files. A failing hook leaves the repository uncommitted. The assistant cannot approve.
- [X] T003 Cover the command in `tests/unit/test_commit_file.py` and `tests/contract/test_commit_api.py`.

## Notes

- A file write, a folder, a test run, and a delete keep their current rules.
- Opening a pull request is a separate later feature.
