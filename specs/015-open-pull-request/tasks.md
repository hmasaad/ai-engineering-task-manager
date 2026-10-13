# Tasks: Open One Pull Request

**Input**: `specs/015-open-pull-request/spec.md`

## Phase 1

- [X] T001 Add `pull_request` and `pull_request_result` to `src/task_manager/storage/schema.sql`. `pull_request.change_id` references `implementation_change(id)` and stores the branch and base branch. `pull_request_result` is inserted only after the pull request opens and stores its address.
- [X] T002 Open one pull request from `src/task_manager/domain/pull_request.py`. Every request waits. Approval pushes `refs/heads/<branch>` to `origin` with no `--force` and no `--no-verify`, then runs `gh pr create` for that branch only. A refusing hook publishes nothing. The assistant cannot approve.
- [X] T003 Cover the command in `tests/unit/test_pull_request.py` and `tests/contract/test_pull_request_api.py`.

## Notes

- A file write, a folder, a test run, a delete, and a commit keep their current rules.
- The remote in tests is a local repository. The command does not contact a hosted repository during tests.
