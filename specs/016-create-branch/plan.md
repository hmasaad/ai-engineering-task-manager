# Implementation Plan: Create One Branch

**Branch**: `016-create-branch` | **Date**: 2026-10-13 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/016-create-branch/spec.md`

## Summary

On an In Progress task, the engineer names one new branch in an existing repository. The request is stored as consequential and waits. Approval creates that branch from the stored commit and checks it out. Opening the task shows the stored branch and does not create or check out again. A commit, a pull request, and the earlier actions keep their current rules.

The work extends the existing Python process. Two new tables only. No new dependency, and no new task status.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI, Uvicorn, Jinja2, pytest. SQLite through `sqlite3`. No new dependency.

**Storage**: The same SQLite workspace file. One table stores the branch name and the commit it starts from. A second table is inserted only after the branch is checked out.

**Testing**: pytest. Unit tests cover one rule at a time. Contract tests cover the HTTP command. Existing commit and pull-request tests stay green.

**Target Platform**: Local machine. The server binds to `127.0.0.1` only.

**Project Type**: Local web application with a domain library in the same process

**Performance Goals**: Recording one branch request and opening the task that holds it each finish in under 200 milliseconds on a workspace of 5,000 tasks. The branch row is read by the change's primary key.

**Constraints**: One workspace, no sign-in. The client cannot choose the assistant name, the engineer name, or the time. Constitution v1.0.0. Specifications 001 through 015 are not rewritten. The command does not call `git config` and does not pass `--force`, `--no-verify`, or `-i`.

**Scale/Scope**: One engineer and one workspace. This feature adds one branch on one In Progress task. It does not add a commit, a pull request, or a task status.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution: `.specify/memory/constitution.md` v1.0.0.

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | The spec names the branch, the starting commit, the refusals, and the approval. |
| II. Test-first verification | Pass | Unit and contract tests cover the waiting request, the checkout, and the refusals. |
| III. Explicit task state | Pass | Task status stays In Progress. Creating the branch does not transition the task. |
| IV. Traceability | Pass | The branch row names the implementation change. The task detail shows the branch and the commit. |
| V. Deterministic behavior | Pass | Approval checks out only when the commit and the absent name still match. Opening the task does not run the command again. |
| VI. Observable AI actions | Pass | The stored change names the workspace assistant, the branch, the commit, and the time. |
| VII. Human approval | Pass | Every request waits. The assistant cannot approve. Decline does not create the branch. |
| VIII. Small, independently verifiable changes | Pass | One workspace feature. It does not rewrite earlier specifications. |

No gate failed. No exception is requested.

## Project Structure

### Documentation (this feature)

```text
specs/016-create-branch/
├── plan.md
├── spec.md
├── tasks.md
└── checklists/
```

### Source Code (repository root)

```text
src/task_manager/domain/branch.py
src/task_manager/storage/schema.sql
src/task_manager/storage/implementation_store.py
src/task_manager/domain/implementation.py
src/task_manager/workspace.py
src/task_manager/web/api.py
src/task_manager/web/pages.py
src/task_manager/web/templates/detail.html
tests/unit/test_branch.py
tests/contract/test_branch_api.py
```

**Structure Decision**: The branch command follows the commit command. The domain function records the request. Approval in the existing change command performs the checkout.
