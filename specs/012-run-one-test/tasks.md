# Tasks: Run One Test

**Input**: `specs/012-run-one-test/spec.md`

## Phase 1

- [X] T001 Add `test_run` and `test_run_result` to `src/task_manager/storage/schema.sql`. `test_run.change_id` references `implementation_change(id)` and stores the named test. `test_run_result` is inserted only when the test has run, with `passed` or `failed` and the output text.
- [X] T002 Run one named test from `src/task_manager/domain/test_run.py` with pytest only: one existing `path::test` inside the project, no shell, and no extra engineer arguments. An ordinary request stores Passed or Failed. A consequential or stopped request waits. Approval runs it once. The assistant cannot approve. Opening the task does not run it again.
- [X] T003 Cover the command in `tests/unit/test_run.py` and `tests/contract/test_run_api.py`.

## Notes

- A requirement result is still recorded only by the engineer. This command does not insert one.
- Deleting a file, committing, and opening a pull request are separate later features.
